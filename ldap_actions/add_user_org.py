#!/usr/bin/env python3

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ldap3 import MODIFY_ADD, MODIFY_DELETE

from ldap_connection import get_connection
import config


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
        print(f"User not found: {email}")
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
        print(f"Organization not found: {org_cn}")
        return

    org_entry = conn.entries[0]

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
                print(f"Removed {user_dn} from {existing_org.entry_dn}")
            except Exception as e:
                print(f"Error removing user from {existing_org.entry_dn}: {e}")

    if "member" in org_entry and user_dn in org_entry.member.values:
        print(f"User already in organization: {org_cn}")
        return

    print(f"Adding {user_dn} to {org_dn}")
    try:
        conn.modify(org_dn, {"member": [(MODIFY_ADD, [user_dn])]})
        print("Organization update successful.")
    except Exception as e:
        print("Error adding user to organization:", e)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python add_user_org.py <email> <ORG_CN>")
        sys.exit(1)

    add_user_to_org(sys.argv[1], sys.argv[2])
