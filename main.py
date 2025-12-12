import logging
import sys
from ldap_actions.ldap_connection import get_connection
import config

logger = logging.getLogger(__name__)

def main():
    if len(sys.argv) < 2:
        logger.debug("Usage: python main.py <email>")
        return

    mail = sys.argv[1]
    conn = get_connection()

    conn.search(
        search_base=config.LDAP_SEARCH_BASE,
        search_filter=f"({config.LDAP_MAIL_ATTRIBUTE}={mail})",
        attributes=["cn", "uid", "memberOf"]
    )

    if not conn.entries:
        logger.debug("User not found.")
        return

    logger.debug(conn.entries[0])

if __name__ == "__main__":
    main()
