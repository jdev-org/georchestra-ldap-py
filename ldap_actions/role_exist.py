#!/usr/bin/env python3

import logging
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ldap_connection import get_connection
import config

logger = logging.getLogger(__name__)

def role_exists(role_cn: str) -> bool:
    """
    Return True if a role exists under ``LDAP_ROLE_DN``.

    Args:
        role_cn (str): Common name of the role to check.
    """
    conn = get_connection()
    conn.search(
        search_base=f"{config.LDAP_ROLE_DN},{config.LDAP_SEARCH_BASE}",
        search_filter=f"(cn={role_cn})",
        attributes=["cn"],
    )
    if conn.entries:
        logger.debug("Role exists: %s", role_cn)
        return True

    logger.debug("Role not found: %s", role_cn)
    return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.debug("Usage: python role_exist.py <ROLE_CN>")
        sys.exit(1)

    role_exists(sys.argv[1])
