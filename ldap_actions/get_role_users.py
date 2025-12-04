#!/usr/bin/env python3

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ldap_connection import get_connection
import config


def get_role_users(role_cn: str):
    """
    Return and print the members (DNs) of a role.

    Args:
        role_cn (str): Common name of the role.
    """
    conn = get_connection()

    role_dn = f"cn={role_cn},{config.LDAP_ROLE_DN},{config.LDAP_SEARCH_BASE}"
    conn.search(
        search_base=role_dn,
        search_filter="(objectClass=*)",
        attributes=["member"],
    )

    if not conn.entries:
        print(f"Role not found: {role_cn}")
        return []

    role_entry = conn.entries[0]
    members = list(role_entry.member.values) if "member" in role_entry else []

    print("=== Role Members ===")
    if members:
        for m in members:
            print(f"- {m}")
    else:
        print("No members")

    return members


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_role_users.py <ROLE_CN>")
        sys.exit(1)

    get_role_users(sys.argv[1])
