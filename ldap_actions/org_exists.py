#!/usr/bin/env python3

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ldap_connection import get_connection
import config


def org_exists(org_cn: str) -> bool:
    """
    Return True if an organization exists under ``LDAP_ORG_DN``.

    Args:
        org_cn (str): Common name of the organization to check.
    """
    conn = get_connection()
    conn.search(
        search_base=f"{config.LDAP_ORG_DN},{config.LDAP_SEARCH_BASE}",
        search_filter=f"(cn={org_cn})",
        attributes=["cn", "o"],
    )

    if conn.entries:
        print(f"Organization exists: {org_cn}")
        return True

    print(f"Organization not found: {org_cn}")
    return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python org_exists.py <ORG_CN>")
        sys.exit(1)

    org_exists(sys.argv[1])
