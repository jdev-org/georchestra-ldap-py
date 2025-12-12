#!/usr/bin/env python3

import logging
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ldap3 import MODIFY_ADD
from ldap_connection import get_connection
import config

logger = logging.getLogger(__name__)

def add_role(email: str, role_cn: str):
    conn = get_connection()

    # 1) Trouver l'utilisateur par email
    conn.search(
        search_base=config.LDAP_SEARCH_BASE,
        search_filter=f"({config.LDAP_MAIL_ATTRIBUTE}={email})",
        search_scope="SUBTREE",
        attributes=[]  # ne pas demander "dn" car ce n'est pas un attribut
    )

    if not conn.entries:
        logger.debug("User not found: %s", email)
        return

    user_dn = conn.entries[0].entry_dn
    logger.debug("User DN found: %s", user_dn)

    # 2) Construire le DN du rôle
    role_dn = f"cn={role_cn},{config.LDAP_ROLE_DN},{config.LDAP_SEARCH_BASE}"

    # 3) Vérifier que le rôle existe
    conn.search(
        search_base=f"{config.LDAP_ROLE_DN},{config.LDAP_SEARCH_BASE}",
        search_filter=f"(cn={role_cn})",
        attributes=["member"]
    )

    if not conn.entries:
        logger.debug("Role not found: %s", role_cn)
        return

    role_entry = conn.entries[0]

    # 3bis) Vérifier si l'utilisateur est déjà membre
    if "member" in role_entry and user_dn in role_entry.member.values:
        logger.debug("User already has role: %s", role_cn)
        return

    logger.debug("Adding user to role: %s", role_dn)

    # 4) Ajouter l'utilisateur au rôle
    try:
        conn.modify(
            role_dn,
            {"member": [(MODIFY_ADD, [user_dn])]}
        )
        logger.debug("Role assignment successful.")
    except Exception as e:
        logger.debug("Error adding user to role: %s", e)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        logger.debug("Usage: python add_user_role.py <email> <role_cn>")
        sys.exit(1)

    add_role(sys.argv[1], sys.argv[2])
