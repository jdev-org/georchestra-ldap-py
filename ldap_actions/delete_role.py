#!/usr/bin/env python3

import logging
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ldap3 import MODIFY_DELETE
from ldap_connection import get_connection
import config

logger = logging.getLogger(__name__)

def delete_role(role_cn: str):
    conn = get_connection()

    role_dn = f"cn={role_cn},{config.LDAP_ROLE_DN},{config.LDAP_SEARCH_BASE}"

    # 1) Vérifier si le rôle existe
    conn.search(
        search_base=f"{config.LDAP_ROLE_DN},{config.LDAP_SEARCH_BASE}",
        search_filter=f"(cn={role_cn})",
        attributes=["member"]
    )

    if not conn.entries:
        logger.debug("Role not found: %s", role_cn)
        return

    role_entry = conn.entries[0]

    # 2) Retirer tous les membres du rôle
    if "member" in role_entry:
        logger.debug("Removing all members from role...")
        for member_dn in role_entry.member.values:
            try:
                conn.modify(
                    role_dn,
                    {"member": [(MODIFY_DELETE, [member_dn])]}
                )
                logger.debug(" - Removed %s", member_dn)
            except Exception as e:
                logger.debug("Error removing member %s: %s", member_dn, e)

    # 3) Supprimer le rôle
    logger.debug("Deleting role: %s", role_dn)
    try:
        conn.delete(role_dn)
        logger.debug("Role successfully deleted.")
    except Exception as e:
        logger.debug("Error deleting role: %s", e)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.debug("Usage: python delete_role.py <role_cn>")
        sys.exit(1)

    delete_role(sys.argv[1])
