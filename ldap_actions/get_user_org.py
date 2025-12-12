#!/usr/bin/env python3

import logging
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ldap_connection import get_connection
import config

logger = logging.getLogger(__name__)

def get_user_org(email: str):
    """
    Return and print the organization CN for a user (by email).

    Args:
        email (str): User email.
    """
    conn = get_connection()

    # Find user
    conn.search(
        search_base=config.LDAP_SEARCH_BASE,
        search_filter=f"({config.LDAP_MAIL_ATTRIBUTE}={email})",
        attributes=["memberOf"],
    )
    if not conn.entries:
        logger.debug("User not found: %s", email)
        return None

    user = conn.entries[0]

    org_suffix = f"{config.LDAP_ORG_DN},{config.LDAP_SEARCH_BASE}"
    org_cn = None

    if "memberOf" in user:
        for group_dn in user.memberOf.values:
            if group_dn.endswith(org_suffix):
                org_cn = group_dn.split(",")[0].split("=")[1]
                break

    logger.debug("=== User Organization ===")
    if org_cn:
        logger.debug(org_cn)
    else:
        logger.debug("No organization found")

    return org_cn


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.debug("Usage: python get_user_org.py <email>")
        sys.exit(1)

    get_user_org(sys.argv[1])
