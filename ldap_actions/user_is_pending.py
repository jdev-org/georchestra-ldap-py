#!/usr/bin/env python3

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ldap_connection import get_connection
import config


def user_is_pending(email: str) -> bool:
    """
    Return True if the user (by email) is located under ``LDAP_PENDING_USERS_DN``.

    Args:
        email (str): User email.
    """
    conn = get_connection()
    conn.search(
        search_base=config.LDAP_SEARCH_BASE,
        search_filter=f"({config.LDAP_MAIL_ATTRIBUTE}={email})",
        search_scope="SUBTREE",
        attributes=["dn"],
    )

    if not conn.entries:
        print(f"User not found: {email}")
        return False

    user_dn = conn.entries[0].entry_dn
    pending_suffix = f"{config.LDAP_PENDING_USERS_DN},{config.LDAP_SEARCH_BASE}"
    is_pending = pending_suffix in user_dn
    print(f"User DN: {user_dn}")
    print(f"Is pending: {is_pending}")
    return is_pending


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python user_is_pending.py <email>")
        sys.exit(1)

    user_is_pending(sys.argv[1])
