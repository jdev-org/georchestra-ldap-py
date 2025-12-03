from __future__ import annotations

import importlib

from georchestra_ldap.config import LdapSettings
from georchestra_ldap.errors import LegacyConfigMissing

# Mapping between the new LdapSettings dataclass and the legacy config.py globals.
_SETTINGS_MAP = {
    "LDAP_SERVER": "server",
    "LDAP_PORT": "port",
    "LDAP_USE_SSL": "use_ssl",
    "LDAP_USER_DN": "user_dn",
    "LDAP_PASSWORD": "password",
    "LDAP_USERS_DN": "users_dn",
    "LDAP_PENDING_USERS_DN": "pending_users_dn",
    "LDAP_ORG_DN": "org_dn",
    "LDAP_ROLE_DN": "role_dn",
    "LDAP_SEARCH_BASE": "search_base",
    "LDAP_MAIL_ATTRIBUTE": "mail_attribute",
    "LDAP_DEFAULT_ROLE_CN": "default_role_cn",
    "LDAP_DEFAULT_ORG_CN": "default_org_cn",
}


def apply_settings_to_legacy_config(settings: LdapSettings) -> None:
    """
    Copy the values from a :class:`LdapSettings` instance into the legacy
    ``config.py`` module used by the historical scripts in ``ldap_actions``.
    """
    try:
        legacy_config = importlib.import_module("config")
    except ModuleNotFoundError as exc:
        if exc.name == "config":
            raise LegacyConfigMissing(
                "config.py must stay importable for the ldap_actions scripts."
            ) from exc
        raise

    for target, source in _SETTINGS_MAP.items():
        setattr(legacy_config, target, getattr(settings, source))
