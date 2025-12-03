import sys
sys.path.append("..") 
from ldap_connection import get_connection
from .. import config

def create_role(role_cn):
    conn = get_connection()
    role_dn = f"cn={role_cn},{config.LDAP_ROLE_DN},{config.LDAP_SEARCH_BASE}"

    conn.search(role_dn, "(objectClass=*)")

    if conn.entries:
        print("Role exists already.")
        return

    conn.add(role_dn, ["groupOfMembers", "top"], {"cn": role_cn, "member": []})
    print(f"Role created: {role_cn}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_role.py <role_cn>")
        exit(1)

    create_role(sys.argv[1])
