#!/usr/bin/env python3

import logging
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ldap_connection import get_connection
import config

logger = logging.getLogger(__name__)

def get_user_infos(email: str):
    """
    Return the ldap3 entry for a user searched by email and print its main attributes.
    """
    conn = get_connection()

    conn.search(
        search_base=config.LDAP_SEARCH_BASE,
        search_filter=f"({config.LDAP_MAIL_ATTRIBUTE}={email})",
        attributes=["cn", "uid", "mail", "memberOf"],
    )

    if not conn.entries:
        logger.debug("User not found.")
        return None

    user = conn.entries[0]

    logger.debug("=== User Information ===")
    logger.debug("DN: %s", user.entry_dn)
    logger.debug("uid: %s", user.uid.value if "uid" in user else None)
    logger.debug("cn: %s", user.cn.value if "cn" in user else None)
    logger.debug("mail: %s", user.mail.value if "mail" in user else None)

    logger.debug("\nGroups (memberOf):")
    if "memberOf" in user:
        for m in user.memberOf.values:
            logger.debug(" - %s", m)
    else:
        logger.debug("No groups")

    return user


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.debug("Usage: python get_user_infos.py <email>")
        sys.exit(1)

    get_user_infos(sys.argv[1])
