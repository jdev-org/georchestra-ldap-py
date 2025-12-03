import sys
sys.path.append("..") 
from ldap_connection import get_connection

def update_lastname(user_dn, new_lastname):
    conn = get_connection()
    conn.modify(user_dn, {"sn": [(conn.MODIFY_REPLACE, [new_lastname])]})
    print(f"Lastname updated to {new_lastname}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python update_user_name.py <user_dn> <lastname>")
        exit(1)

    update_lastname(sys.argv[1], sys.argv[2])
