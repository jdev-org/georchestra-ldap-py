"""
Example script based on ``examples/example_alice_flow.py`` that shows how to
override LDAP connection settings before creating the client.

Customizes the equivalent of the environment variables ``LDAP_SERVER``,
``LDAP_PORT`` and ``LDAP_PASSWORD``.
"""

import logging

from georchestra_ldap import GeorchestraLdapClient, LdapSettings

logger = logging.getLogger(__name__)


def user_exists(client: GeorchestraLdapClient, email: str) -> str | None:
    """Return the DN of the user if found, else None."""
    conn = client.get_connection()
    settings = client.settings
    conn.search(
        search_base=settings.search_base,
        search_filter=f"({settings.mail_attribute}={email})",
        attributes=["uid"],
    )
    return conn.entries[0].entry_dn if conn.entries else None


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    # custom config here
    settings = LdapSettings.from_env()
    settings.server = "ldap://ldap.example.org"
    settings.port = 10389
    settings.password = "SuperSecretPassword!"
    # create LDAP client
    client = GeorchestraLdapClient(settings)
    email = "alice@fake.fr"

    logger.debug(
        "Connecting to %s:%s with custom password", settings.server, settings.port
    )

    logger.debug("1) Ensure role FOO exists")
    client.create_role("FOO", "Example role for Alice")

    logger.debug("2) Lookup user %s", email)
    dn = user_exists(client, email)
    if dn:
        logger.debug("   User already exists: %s", dn)
    else:
        logger.debug("3) Create user in pendingusers")
        client.create_user("alice", email, "Alice", "Example", "ChangeMe123!")

    logger.debug("4) Moderate user (pending -> users)")
    client.moderate_user(email)


if __name__ == "__main__":
    main()
