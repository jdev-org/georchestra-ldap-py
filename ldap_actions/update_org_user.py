import sys
sys.path.append("..") 
from ldap_connection import get_connection
from .. import config

def update_user_org(user_dn, org_cn):
    conn = get_connection()

    org_group_dn = f"cn={org_cn},{config.LDAP_ORG_DN},{config.LDAP_SEARCH_BASE}"

    conn.modify(org_group_dn, {
        "member": [(conn.MODIFY_ADD, [user_dn])]
    })
    print(f"User added to org {org_cn}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python update_org_user.py <user_dn> <org_cn>")
        exit(1)

    update_user_org(sys.argv[1], sys.argv[2])
