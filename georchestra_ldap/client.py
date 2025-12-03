from __future__ import annotations

from typing import Iterable

from georchestra_ldap.config import LdapSettings
from georchestra_ldap.utils import apply_settings_to_legacy_config

# Direct imports of the legacy scripts: simple and explicit.
from ldap_actions import (
    add_user_role,
    create_org,
    create_role,
    create_user,
    delete_role,
    delete_user,
    ldap_connection,
    moderate_user,
    read_user_infos,
    read_user_roles,
    remove_user_role,
    update_org_user,
    update_user_name,
)


class GeorchestraLdapClient:
    """
    Thin wrapper around the historical scripts located in ``ldap_actions`` so they
    can be consumed as a reusable API from Python code without touching them.
    """

    def __init__(self, settings: LdapSettings | None = None):
        self.settings = settings or LdapSettings.from_env()
        self._apply_settings()

    def _apply_settings(self) -> None:
        apply_settings_to_legacy_config(self.settings)

    def reload_settings(self, settings: LdapSettings | None = None) -> "GeorchestraLdapClient":
        """
        Update the underlying ``config.py`` values, optionally replacing the
        current :class:`LdapSettings` instance.
        """
        if settings is not None:
            self.settings = settings
        self._apply_settings()
        return self

    def get_connection(self):
        self._apply_settings()
        return ldap_connection.get_connection()

    def create_org(self, org_cn: str, org_name: str | None = None):
        self._apply_settings()
        return create_org.create_org(org_cn, org_name)

    def create_user(self, uid: str, email: str, given_name: str, sn: str, password: str):
        self._apply_settings()
        return create_user.create_user(uid, email, given_name, sn, password)

    def moderate_user(self, email: str):
        self._apply_settings()
        return moderate_user.moderate_user(email)

    def add_user_role(self, email: str, role_cn: str):
        self._apply_settings()
        return add_user_role.add_role(email, role_cn)

    def remove_user_role(self, email: str, role_cn: str):
        self._apply_settings()
        return remove_user_role.remove_role(email, role_cn)

    def create_role(self, role_cn: str, description: str = "Role created via script", members: Iterable[str] | None = None):
        self._apply_settings()
        return create_role.create_role(role_cn, description, members)

    def delete_role(self, role_cn: str):
        self._apply_settings()
        return delete_role.delete_role(role_cn)

    def update_user_org(self, user_dn: str, org_cn: str):
        self._apply_settings()
        return update_org_user.update_user_org(user_dn, org_cn)

    def update_lastname(self, user_dn: str, new_lastname: str):
        self._apply_settings()
        return update_user_name.update_lastname(user_dn, new_lastname)

    def delete_user(self, email: str):
        self._apply_settings()
        return delete_user.delete_user(email)

    def read_user_infos(self, email: str):
        self._apply_settings()
        return read_user_infos.read_user_infos(email)

    def read_user_roles(self, email: str):
        self._apply_settings()
        return read_user_roles.read_user_roles(email)
