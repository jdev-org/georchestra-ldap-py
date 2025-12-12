import logging
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ldap_connection import get_connection
import config

logger = logging.getLogger(__name__)

def update_user_org(user_dn, org_cn):
    conn = get_connection()

    org_group_dn = f"cn={org_cn},{config.LDAP_ORG_DN},{config.LDAP_SEARCH_BASE}"

    conn.modify(org_group_dn, {
        "member": [(conn.MODIFY_ADD, [user_dn])]
    })
    logger.debug("User added to org %s", org_cn)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        logger.debug("Usage: python update_org_user.py <user_dn> <org_cn>")
        exit(1)

    update_user_org(sys.argv[1], sys.argv[2])
