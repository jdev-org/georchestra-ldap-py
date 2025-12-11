"""
Example script that reuses the legacy ldap_actions through the GeorchestraLdapClient.

Steps:
1. Create role FOO if it does not exist.
2. Check if user alice@fake.fr exists.
3. Create the user in pending if missing.
4. Moderate the user (pending -> users).
"""

import logging

from georchestra_ldap import GeorchestraLdapClient

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
    client = GeorchestraLdapClient()  # settings read from env variables by default
    email = "alice@fake.fr"

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
