#!/usr/bin/env python3

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ldap_connection import get_connection
import config


def get_org_users(org_cn: str):
    """
    Return and print the members (DNs) of an organization.

    Args:
        org_cn (str): Common name of the organization.
    """
    conn = get_connection()

    org_dn = f"cn={org_cn},{config.LDAP_ORG_DN},{config.LDAP_SEARCH_BASE}"
    conn.search(
        search_base=org_dn,
        search_filter="(objectClass=*)",
        attributes=["member"],
    )

    if not conn.entries:
        print(f"Organization not found: {org_cn}")
        return []

    org_entry = conn.entries[0]
    members = list(org_entry.member.values) if "member" in org_entry else []

    print("=== Organization Members ===")
    if members:
        for m in members:
            print(f"- {m}")
    else:
        print("No members")

    return members


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_org_users.py <ORG_CN>")
        sys.exit(1)

    get_org_users(sys.argv[1])
