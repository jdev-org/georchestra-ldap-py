import logging
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ldap_connection import get_connection
import config

logger = logging.getLogger(__name__)

def update_lastname(user_dn, new_lastname):
    conn = get_connection()
    conn.modify(user_dn, {"sn": [(conn.MODIFY_REPLACE, [new_lastname])]})
    logger.debug("Lastname updated to %s", new_lastname)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        logger.debug("Usage: python update_user_name.py <user_dn> <lastname>")
        exit(1)

    update_lastname(sys.argv[1], sys.argv[2])
