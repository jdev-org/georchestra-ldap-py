#!/usr/bin/env python3
import logging
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ldap_connection import get_connection
import config

logger = logging.getLogger(__name__)

def read_user_infos(email):
    conn = get_connection()

    conn.search(
        search_base=config.LDAP_SEARCH_BASE,
        search_filter=f"({config.LDAP_MAIL_ATTRIBUTE}={email})",
        attributes=["cn", "uid", "mail", "memberOf"]
    )

    if not conn.entries:
        logger.debug("User not found.")
        return

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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.debug("Usage: python read_user_infos.py <email>")
        exit(1)

    read_user_infos(sys.argv[1])
