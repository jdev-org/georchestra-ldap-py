import sys
sys.path.append("..") 
from ldap_connection import get_connection
from .. import config

def add_role(user_dn, role_cn):
    conn = get_connection()

    role_dn = f"cn={role_cn},{config.LDAP_ROLE_DN},{config.LDAP_SEARCH_BASE}"

    conn.modify(role_dn, {
        "member": [(conn.MODIFY_ADD, [user_dn])]
    })

    print(f"Role {role_cn} added to {user_dn}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python add_user_role.py <user_dn> <role_cn>")
        exit(1)

    add_role(sys.argv[1], sys.argv[2])
