#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ldap_connection import get_connection
import config

def read_user_infos(email):
    conn = get_connection()

    conn.search(
        search_base=config.LDAP_SEARCH_BASE,
        search_filter=f"({config.LDAP_MAIL_ATTRIBUTE}={email})",
        attributes=["cn", "uid", "mail", "memberOf"]
    )

    if not conn.entries:
        print("User not found.")
        return

    user = conn.entries[0]

    print("=== User Information ===")
    print(f"DN: {user.entry_dn}")
    print(f"uid: {user.uid.value if 'uid' in user else None}")
    print(f"cn: {user.cn.value if 'cn' in user else None}")
    print(f"mail: {user.mail.value if 'mail' in user else None}")

    print("\nGroups (memberOf):")
    if "memberOf" in user:
        for m in user.memberOf.values:
            print(f" - {m}")
    else:
        print("No groups")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python read_user_infos.py <email>")
        exit(1)

    read_user_infos(sys.argv[1])
