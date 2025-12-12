#!/usr/bin/env python3

import logging
import sys, os, uuid, hashlib, base64
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ldap3 import MODIFY_ADD
from ldap_connection import get_connection
import config

logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """Retourne un mot de passe LDAP au format SSHA."""
    salt = os.urandom(4)
    sha = hashlib.sha1(password.encode("utf-8"))
    sha.update(salt)
    digest = sha.digest() + salt
    return "{SSHA}" + base64.b64encode(digest).decode()


def create_user(uid: str, email: str, given_name: str, sn: str, password: str):
    conn = get_connection()

    user_dn = f"uid={uid},ou=pendingusers,{config.LDAP_SEARCH_BASE}"

    # Vérifier si l'utilisateur existe déjà
    conn.search(
        search_base=config.LDAP_SEARCH_BASE,
        search_filter=f"(uid={uid})",
        search_scope="SUBTREE",
        attributes=["uid"]
    )
    if conn.entries:
        logger.debug("User already exists: %s", uid)
        return

    # Générer un UUID geOrchestra
    uuid_value = str(uuid.uuid4())

    # Hash du password
    hashed_pwd = hash_password(password)

    attributes = {
        "objectClass": [
            "georchestraUser",
            "organizationalPerson",
            "inetOrgPerson",
            "person",
            "shadowAccount",
            "top"
        ],
        "uid": uid,
        "mail": email,
        "cn": uid,
        "sn": sn,
        "givenName": given_name,
        "description": "USER",
        "knowledgeInformation": f"Auto-created ({uid})",
        "georchestraObjectIdentifier": uuid_value,
        "userPassword": hashed_pwd
    }

    logger.debug("Creating user: %s", user_dn)

    try:
        conn.add(user_dn, attributes=attributes)
        logger.debug("User successfully created in ou=pendingusers.")
    except Exception as e:
        logger.debug("Error while creating user: %s", e)
        return

    # === Ajouter USER role ===
    user_role_dn = f"cn=USER,{config.LDAP_ROLE_DN},{config.LDAP_SEARCH_BASE}"
    logger.debug("Adding user to USER role \u2192 %s", user_role_dn)
    try:
        conn.modify(user_role_dn, {"member": [(MODIFY_ADD, [user_dn])]})
        logger.debug("Added USER role.")
    except Exception as e:
        logger.debug("Error adding USER role: %s", e)

    # === Ajouter organization C2C ===
    org_dn = f"cn=C2C,{config.LDAP_ORG_DN},{config.LDAP_SEARCH_BASE}"
    logger.debug("Adding user to organization C2C \u2192 %s", org_dn)
    try:
        conn.modify(org_dn, {"member": [(MODIFY_ADD, [user_dn])]})
        logger.debug("Added to organization C2C.")
    except Exception as e:
        logger.debug("Error adding organization C2C: %s", e)

    return user_dn


if __name__ == "__main__":
    if len(sys.argv) < 6:
        logger.debug("Usage: python create_user.py <uid> <email> <givenName> <sn> <password>")
        sys.exit(1)

    _, uid, email, given, sn, pwd = sys.argv
    create_user(uid, email, given, sn, pwd)
