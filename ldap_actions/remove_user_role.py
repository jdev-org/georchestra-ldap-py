#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ldap3 import MODIFY_DELETE
from ldap_connection import get_connection
import config


def remove_role(user_dn: str, role_cn: str):
    conn = get_connection()

    role_dn = f"cn={role_cn},{config.LDAP_ROLE_DN},{config.LDAP_SEARCH_BASE}"

    # Vérifier que le rôle existe
    conn.search(
        search_base=f"{config.LDAP_ROLE_DN},{config.LDAP_SEARCH_BASE}",
        search_filter=f"(cn={role_cn})",
        attributes=["member"]
    )

    if not conn.entries:
        print(f"Role not found: {role_cn}")
        return

    print(f"Removing {user_dn} from role {role_dn}")

    try:
        conn.modify(
            role_dn,
            {"member": [(MODIFY_DELETE, [user_dn])]}
        )
        print("Role removal successful.")
    except Exception as e:
        print("Error removing user from role:", e)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python remove_user_role.py <user_dn> <role_cn>")
        sys.exit(1)

    remove_role(sys.argv[1], sys.argv[2])
