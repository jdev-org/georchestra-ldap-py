#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ldap3 import MODIFY_DELETE
from ldap_connection import get_connection
import config


def delete_role(role_cn: str):
    conn = get_connection()

    role_dn = f"cn={role_cn},{config.LDAP_ROLE_DN},{config.LDAP_SEARCH_BASE}"

    # 1) Vérifier si le rôle existe
    conn.search(
        search_base=f"{config.LDAP_ROLE_DN},{config.LDAP_SEARCH_BASE}",
        search_filter=f"(cn={role_cn})",
        attributes=["member"]
    )

    if not conn.entries:
        print(f"Role not found: {role_cn}")
        return

    role_entry = conn.entries[0]

    # 2) Retirer tous les membres du rôle
    if "member" in role_entry:
        print("Removing all members from role...")
        for member_dn in role_entry.member.values:
            try:
                conn.modify(
                    role_dn,
                    {"member": [(MODIFY_DELETE, [member_dn])]}
                )
                print(f" - Removed {member_dn}")
            except Exception as e:
                print(f"Error removing member {member_dn}: {e}")

    # 3) Supprimer le rôle
    print(f"Deleting role: {role_dn}")
    try:
        conn.delete(role_dn)
        print("Role successfully deleted.")
    except Exception as e:
        print("Error deleting role:", e)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python delete_role.py <role_cn>")
        sys.exit(1)

    delete_role(sys.argv[1])
