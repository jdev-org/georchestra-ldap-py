"""
Example flow:
1. Look up user alice@fake.fr.
2. Create the user in pending if missing, then moderate (pending -> users).
3. Read the user's roles.
4. Ensure roles FOO and BAZ exist and assign them.
5. Remove role BAZ from the user (keeps role entry intact).
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
    client = GeorchestraLdapClient()  # reads settings from env by default
    email = "alice@fake.fr"
    uid = "alice"

    logger.info("1) Lookup user %s", email)
    dn = user_exists(client, email)
    if dn:
        logger.info("   User already exists: %s", dn)
    else:
        logger.info("2) Create user in pendingusers")
        client.create_user(uid, email, "Alice", "Example", "ChangeMe123!")

    logger.info("3) Moderate user (pending -> users if needed)")
    client.moderate_user(email)

    logger.info("4) Current roles for user")
    client.read_user_roles(email)

    logger.info("5) Ensure roles FOO and BAZ exist and assign them")
    for role in ("FOO", "BAZ"):
        client.create_role(role, f"Example role {role}")  # idempotent if already exists
        client.add_user_role(email, role)

    logger.info("6) Remove role BAZ from user")
    client.remove_user_role(email, "BAZ")


if __name__ == "__main__":
    main()
