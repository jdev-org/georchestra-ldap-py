#!/usr/bin/env python3

import logging
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ldap_connection import get_connection
import config

logger = logging.getLogger(__name__)

def get_role_infos(role_cn: str):
    """
    Return the ldap3 entry for a role searched by cn and print its attributes/members.
    """
    conn = get_connection()

    conn.search(
        search_base=f"{config.LDAP_ROLE_DN},{config.LDAP_SEARCH_BASE}",
        search_filter=f"(cn={role_cn})",
        attributes=["cn", "description", "member"],
    )

    if not conn.entries:
        logger.debug("Role not found: %s", role_cn)
        return None

    role = conn.entries[0]

    logger.debug("=== Role Information ===")
    logger.debug("DN: %s", role.entry_dn)
    logger.debug("cn: %s", role.cn.value if "cn" in role else None)
    logger.debug("description: %s", role.description.value if "description" in role else None)

    logger.debug("\nMembers:")
    if "member" in role:
        for m in role.member.values:
            logger.debug(" - %s", m)
    else:
        logger.debug("No members")

    return role


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.debug("Usage: python get_role_infos.py <ROLE_CN>")
        sys.exit(1)

    get_role_infos(sys.argv[1])
