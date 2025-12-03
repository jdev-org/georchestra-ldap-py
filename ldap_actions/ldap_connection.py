from ldap3 import Server, Connection, ALL
import sys, os

# Ajoute le dossier parent (où se trouve config.py)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import config

def get_connection():
    server = Server(
        config.LDAP_SERVER,
        port=config.LDAP_PORT,
        use_ssl=config.LDAP_USE_SSL,
        get_info=ALL
    )

    conn = Connection(
        server,
        user=config.LDAP_USER_DN,
        password=config.LDAP_PASSWORD,
        auto_bind=True
    )
    return conn
