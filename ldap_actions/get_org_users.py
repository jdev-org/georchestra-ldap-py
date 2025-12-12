#!/usr/bin/env python3

import logging
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ldap_connection import get_connection
import config

logger = logging.getLogger(__name__)

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
        logger.debug("Organization not found: %s", org_cn)
        return []

    org_entry = conn.entries[0]
    members = list(org_entry.member.values) if "member" in org_entry else []

    logger.debug("=== Organization Members ===")
    if members:
        for m in members:
            logger.debug("- %s", m)
    else:
        logger.debug("No members")

    return members


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.debug("Usage: python get_org_users.py <ORG_CN>")
        sys.exit(1)

    get_org_users(sys.argv[1])
