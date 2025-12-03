from ldap3 import Server, Connection, ALL
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
