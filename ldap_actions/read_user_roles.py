#!/usr/bin/env python3

import logging
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ldap_connection import get_connection
import config

logger = logging.getLogger(__name__)

def read_user_roles(email):
    conn = get_connection()

    # 1) trouver l'utilisateur
    conn.search(
        search_base=config.LDAP_SEARCH_BASE,
        search_filter=f"({config.LDAP_MAIL_ATTRIBUTE}={email})",
        attributes=["memberOf"]
    )

    if not conn.entries:
        logger.debug("User not found.")
        return

    user = conn.entries[0]

    # 2) filtrer uniquement les rôles = groupes sous ou=roles
    roles = []
    if "memberOf" in user:
        role_suffix = f"{config.LDAP_ROLE_DN},{config.LDAP_SEARCH_BASE}"
        for group_dn in user.memberOf.values:
            if group_dn.endswith(role_suffix):
                # group_dn = "cn=ADMIN,ou=roles,dc=georchestra,dc=org"
                role_cn = group_dn.split(",")[0].split("=")[1]
                roles.append(role_cn)

    logger.debug("=== User Roles ===")
    if roles:
        for r in roles:
            logger.debug("- %s", r)
    else:
        logger.debug("No roles")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.debug("Usage: python read_user_roles.py <email>")
        exit(1)

    read_user_roles(sys.argv[1])
