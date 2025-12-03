import sys
sys.path.append("..") 
from ldap_connection import get_connection
from .. import config

def create_org(org_cn, org_name=None):
    conn = get_connection()
    org_dn = f"cn={org_cn},{config.LDAP_ORG_DN},{config.LDAP_SEARCH_BASE}"

    conn.search(org_dn, "(objectClass=*)")

    if conn.entries:
        print("Organization exists already.")
        return

    attrs = {
        "cn": org_cn,
        "o": org_name if org_name else org_cn
    }

    conn.add(org_dn, ["groupOfMembers", "top", "georchestraOrg"], attrs)
    print(f"Organization created: {org_cn}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_org.py <org_cn> [name]")
        exit(1)

    create_org(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
