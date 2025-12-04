from __future__ import annotations

import logging
from typing import Iterable

from georchestra_ldap.config import LdapSettings
from georchestra_ldap.utils import apply_settings_to_legacy_config, ensure_legacy_import_aliases

# Direct imports of the legacy scripts: simple and explicit.
from ldap_actions import (
    add_user_role,
    add_user_org,
    create_org,
    create_role,
    create_user,
    delete_role,
    delete_user,
    get_org_users,
    get_role_infos,
    get_role_users,
    get_user_infos,
    get_user_roles,
    get_user_org,
    ldap_connection,
    moderate_user,
    org_exists,
    read_user_infos,
    read_user_roles,
    remove_user_role,
    role_exist,
    update_org_user,
    update_user_name,
    user_is_pending,
)

logger = logging.getLogger(__name__)


class GeorchestraLdapClient:
    """
    Thin wrapper around the historical scripts in ``ldap_actions`` with a simple,
    importable API. Each method delegates to the matching legacy script while
    reapplying :class:`LdapSettings` to the legacy ``config.py``.

    Common usage example :
    ----------------------
    >>> from georchestra_ldap import GeorchestraLdapClient, LdapSettings
    >>> 
    >>> client = GeorchestraLdapClient(LdapSettings.from_env())
    >>> 
    >>> client.create_role("FOO")
    >>> 
    >>> client.create_user("alice", "alice@example.org", "Alice", "Example", "pwd")
    >>> 
    >>> client.moderate_user("alice@example.org")
    >>> 
    >>> client.add_user_role("alice@example.org", "FOO")
    >>> 
    >>> client.read_user_roles("alice@example.org")
    >>> 
    >>> client.delete_user("alice@example.org")
    """

    def __init__(self, settings: LdapSettings | None = None):
        self.settings = settings or LdapSettings.from_env()
        self._apply_settings()

    def _apply_settings(self) -> None:
        apply_settings_to_legacy_config(self.settings)
        ensure_legacy_import_aliases()

    def _run(self, action_name: str, func, *args, **kwargs):
        """
        Apply settings, log the action, call the legacy function.

        Args:
            action_name (str): Friendly action name used for logging.
            func (callable): Legacy function to execute.
            *args: Positional arguments forwarded to the underlying function.
            **kwargs: Keyword arguments forwarded to the underlying function.
        """
        self._apply_settings()
        logger.info("Running action: %s", action_name)
        try:
            return func(*args, **kwargs)
        except Exception:
            logger.exception("Action failed: %s", action_name)
            raise

    def reload_settings(self, settings: LdapSettings | None = None) -> "GeorchestraLdapClient":
        """
        Update the underlying ``config.py`` values, optionally replacing the
        current :class:`LdapSettings` instance.

        Args:
            settings (LdapSettings | None): New settings to apply; if None, reapply the existing instance.
        """
        if settings is not None:
            self.settings = settings
        self._apply_settings()
        return self

    def get_connection(self):
        """
        Return an auto-bound ldap3 Connection configured from current settings.
        """
        return self._run("get_connection", ldap_connection.get_connection)

    def create_org(self, org_cn: str, org_name: str | None = None):
        """
        Create an organization if it does not exist.

        Args:
            org_cn (str): Common name of the organization.
            org_name (str | None): Optional display name (defaults to ``org_cn``).
        """
        return self._run("create_org", create_org.create_org, org_cn, org_name)

    def create_user(self, uid: str, email: str, given_name: str, sn: str, password: str):
        # Do not log password, so only log action name above.
        """
        Create a pending user with geOrchestra objectClasses, USER role, C2C org.

        Args:
            uid (str): LDAP uid.
            email (str): User email.
            given_name (str): Given name.
            sn (str): Surname.
            password (str): Plain password, hashed before being stored.
        """
        return self._run("create_user", create_user.create_user, uid, email, given_name, sn, password)

    def moderate_user(self, email: str):
        """
        Move a user from pending to users if present in pending.
        """
        return self._run("moderate_user", moderate_user.moderate_user, email)

    def add_user_role(self, email: str, role_cn: str):
        """
        Add an existing role to the user identified by email.
        """
        return self._run("add_user_role", add_user_role.add_role, email, role_cn)

    def add_user_org(self, email: str, org_cn: str):
        """
        Add a user (by email) to an organization, removing them from other orgs first.

        Args:
            email (str): User email.
            org_cn (str): Organization common name.
        """
        return self._run("add_user_org", add_user_org.add_user_to_org, email, org_cn)

    def remove_user_role(self, email: str, role_cn: str):
        """
        Remove a role from the user identified by email.
        """
        return self._run("remove_user_role", remove_user_role.remove_role, email, role_cn)

    def create_role(self, role_cn: str, description: str = "Role created via script", members: Iterable[str] | None = None):
        """
        Create a role if missing (idempotent); optionally seed members.
        """
        return self._run("create_role", create_role.create_role, role_cn, description, members)

    def delete_role(self, role_cn: str):
        """
        Delete a role after removing its members.
        """
        return self._run("delete_role", delete_role.delete_role, role_cn)

    def update_user_org(self, user_dn: str, org_cn: str):
        """
        Add a user DN to the given organization group.
        """
        return self._run("update_user_org", update_org_user.update_user_org, user_dn, org_cn)

    def update_lastname(self, user_dn: str, new_lastname: str):
        """
        Replace the ``sn`` attribute of a user DN.
        """
        return self._run("update_lastname", update_user_name.update_lastname, user_dn, new_lastname)

    def delete_user(self, email: str):
        """
        Remove a user from all roles/orgs then delete the entry.
        """
        return self._run("delete_user", delete_user.delete_user, email)

    def read_user_infos(self, email: str):
        """
        Print full user info (DN, uid, cn, mail, memberOf).
        """
        return self._run("read_user_infos", read_user_infos.read_user_infos, email)

    def read_user_roles(self, email: str):
        """
        Print roles (groups under roles DN) for a user email.
        """
        return self._run("read_user_roles", read_user_roles.read_user_roles, email)

    def get_user_infos(self, email: str):
        """
        Return and print user information (DN, uid, cn, mail, memberOf).

        Args:
            email (str): User email.
        """
        return self._run("get_user_infos", get_user_infos.get_user_infos, email)

    def get_role_infos(self, role_cn: str):
        """
        Return and print role information (DN, cn, description, members).

        Args:
            role_cn (str): Common name of the role.
        """
        return self._run("get_role_infos", get_role_infos.get_role_infos, role_cn)

    def get_user_roles(self, email: str):
        """
        Return and print the list of role CNs for a given user email.

        Args:
            email (str): User email.
        """
        return self._run("get_user_roles", get_user_roles.get_user_roles, email)

    def get_user_org(self, email: str):
        """
        Return and print the organization CN for a given user email.

        Args:
            email (str): User email.
        """
        return self._run("get_user_org", get_user_org.get_user_org, email)

    def role_exists(self, role_cn: str) -> bool:
        """
        Return True if a role exists under the configured roles DN.

        Args:
            role_cn (str): Common name of the role to check.
        """
        return self._run("role_exists", role_exist.role_exists, role_cn)

    def get_role_users(self, role_cn: str):
        """
        Return and print the members (DNs) of a role.

        Args:
            role_cn (str): Common name of the role.
        """
        return self._run("get_role_users", get_role_users.get_role_users, role_cn)

    def org_exists(self, org_cn: str) -> bool:
        """
        Return True if an organization exists under the configured orgs DN.

        Args:
            org_cn (str): Common name of the organization to check.
        """
        return self._run("org_exists", org_exists.org_exists, org_cn)

    def get_org_users(self, org_cn: str):
        """
        Return and print the members (DNs) of an organization.

        Args:
            org_cn (str): Common name of the organization.
        """
        return self._run("get_org_users", get_org_users.get_org_users, org_cn)

    def user_is_pending(self, email: str) -> bool:
        """
        Return True if the user (by email) is in pending users.

        Args:
            email (str): User email.
        """
        return self._run("user_is_pending", user_is_pending.user_is_pending, email)
