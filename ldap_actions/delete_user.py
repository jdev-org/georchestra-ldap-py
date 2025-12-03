#!/usr/bin/env python3

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ldap_connection import get_connection
import config


def delete_user(email: str):
    conn = get_connection()

    # 1) Trouver l'utilisateur par email
    conn.search(
        search_base=config.LDAP_SEARCH_BASE,
        search_filter=f"({config.LDAP_MAIL_ATTRIBUTE}={email})",
        search_scope="SUBTREE",
        attributes=["uid", "memberOf"]
    )

    if not conn.entries:
        print(f"User not found: {email}")
        return

    user = conn.entries[0]
    user_dn = user.entry_dn

    print(f"Found user: {user_dn}")

    # 2) Retirer l'utilisateur de tous ses rôles
    if "memberOf" in user:
        print("Removing user from roles...")
        for role_dn in user.memberOf.values:
            try:
                conn.modify(
                    role_dn,
                    {"member": [(conn.MODIFY_DELETE, [user_dn])]}
                )
                print(f" - Removed from {role_dn}")
            except Exception as e:
                print(f"Error removing from {role_dn}: {e}")

    # 3) Supprimer l'utilisateur
    print(f"Deleting user entry: {user_dn}")
    try:
        conn.delete(user_dn)
        print("User successfully deleted.")
    except Exception as e:
        print("Error deleting user:", e)
        return

    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python delete_user.py <email>")
        sys.exit(1)

    delete_user(sys.argv[1])
