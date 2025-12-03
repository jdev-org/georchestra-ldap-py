#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ldap_connection import get_connection
import config


def moderate_user(email: str):
    conn = get_connection()

    # 1) Trouver l'utilisateur par email
    conn.search(
        search_base=config.LDAP_SEARCH_BASE,
        search_filter=f"({config.LDAP_MAIL_ATTRIBUTE}={email})",
        search_scope="SUBTREE",
        attributes=["uid"]
    )

    if not conn.entries:
        print(f"User not found: {email}")
        return

    user = conn.entries[0]
    old_dn = user.entry_dn

    print(f"Found user: {old_dn}")

    # 2) Vérifier qu'il est bien en pending
    if "ou=pendingusers" not in old_dn:
        print("User is NOT in ou=pendingusers — nothing to do.")
        return

    uid = user.uid.value

    # 3) Construire le DN cible avec la config correcte
    new_superior = f"{config.LDAP_USERS_DN},{config.LDAP_SEARCH_BASE}"
    new_dn = f"uid={uid},{new_superior}"

    print(f"Activating user → moving to: {new_dn}")

    # 4) Déplacer l'utilisateur
    try:
        conn.modify_dn(
            dn=old_dn,
            relative_dn=f"uid={uid}",
            new_superior=new_superior
        )
        print("User successfully moved to ou=users.")
    except Exception as e:
        print("Error while moving user:", e)
        return

    return new_dn


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python moderate_user.py <email>")
        sys.exit(1)

    moderate_user(sys.argv[1])
