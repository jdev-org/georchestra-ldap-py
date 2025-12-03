#!/usr/bin/env python3

import sys, os, uuid
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ldap_connection import get_connection
import config


def create_role(role_cn: str, description: str = "Role created via script", members=None):
    conn = get_connection()

    role_dn = f"cn={role_cn},{config.LDAP_ROLE_DN},{config.LDAP_SEARCH_BASE}"

    # Vérifier si le rôle existe déjà
    conn.search(
        search_base=f"{config.LDAP_ROLE_DN},{config.LDAP_SEARCH_BASE}",
        search_filter=f"(cn={role_cn})",
        attributes=["cn"]
    )

    if conn.entries:
        print(f"Role already exists: {role_cn}")
        return role_dn

    if members is None:
        members = []

    # UUID geOrchestra
    uuid_value = str(uuid.uuid4())

    attributes = {
        "objectClass": [
            "top",
            "groupOfMembers",
            "georchestraRole"
        ],
        "cn": role_cn,
        "description": description,
        "georchestraObjectIdentifier": uuid_value
    }

    if members:
        attributes["member"] = members

    print(f"Creating role: {role_dn}")

    try:
        conn.add(role_dn, attributes=attributes)
        print("Role successfully created.")
    except Exception as e:
        print("Error while creating role:", e)
        return None

    return role_dn


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_role.py <ROLE_CN> [description]")
        sys.exit(1)

    role_cn = sys.argv[1]
    description = sys.argv[2] if len(sys.argv) > 2 else "Role created via script"

    create_role(role_cn, description)
