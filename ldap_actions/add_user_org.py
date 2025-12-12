#!/usr/bin/env python3

import sys
import os
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ldap3 import MODIFY_ADD, MODIFY_DELETE

from ldap_connection import get_connection
import config

logger = logging.getLogger(__name__)

def add_user_to_org(email: str, org_cn: str):
    """
    Add a user (by email) to an organization group.

    Args:
        email (str): User email.
        org_cn (str): Organization common name.
    """
    conn = get_connection()

    # Find user DN by email
    conn.search(
        search_base=config.LDAP_SEARCH_BASE,
        search_filter=f"({config.LDAP_MAIL_ATTRIBUTE}={email})",
        attributes=[],
    )
    if not conn.entries:
        logger.debug("User not found: %s", email)
        return

    user_dn = conn.entries[0].entry_dn
    org_dn = f"cn={org_cn},{config.LDAP_ORG_DN},{config.LDAP_SEARCH_BASE}"

    # Check org exists
    conn.search(
        search_base=f"{config.LDAP_ORG_DN},{config.LDAP_SEARCH_BASE}",
        search_filter=f"(cn={org_cn})",
        attributes=["member"],
    )
    if not conn.entries:
        logger.debug("Organization not found: %s", org_cn)
        return

    org_entry = conn.entries[0]

    # If already in target org, do nothing.
    if "member" in org_entry and user_dn in org_entry.member.values:
        logger.debug("User already in organization: %s", org_cn)
        return

    # Remove user from any other orgs first
    conn.search(
        search_base=f"{config.LDAP_ORG_DN},{config.LDAP_SEARCH_BASE}",
        search_filter=f"(member={user_dn})",
        attributes=["member"],
    )
    for existing_org in conn.entries:
        if existing_org.entry_dn != org_dn and "member" in existing_org:
            try:
                conn.modify(existing_org.entry_dn, {"member": [(MODIFY_DELETE, [user_dn])]})
                logger.debug("Removed %s from %s", user_dn, existing_org.entry_dn)
            except Exception as e:
                logger.debug("Error removing user from %s: %s", existing_org.entry_dn, e)

    logger.debug("Adding %s to %s", user_dn, org_dn)
    try:
        conn.modify(org_dn, {"member": [(MODIFY_ADD, [user_dn])]})
        logger.debug("Organization update successful.")
    except Exception as e:
        logger.debug("Error adding user to organization: %s", e)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        logger.debug("Usage: python add_user_org.py <email> <ORG_CN>")
        sys.exit(1)

    add_user_to_org(sys.argv[1], sys.argv[2])
