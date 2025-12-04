# Ensure legacy aliases are registered before importing the client, so imports
# like ``import ldap_connection`` inside ldap_actions work after packaging.
from georchestra_ldap.utils import ensure_legacy_import_aliases as _ensure_aliases

_ensure_aliases()

from georchestra_ldap.client import GeorchestraLdapClient
from georchestra_ldap.config import LdapSettings
from georchestra_ldap.errors import LegacyConfigMissing, LegacyScriptsMissing
from georchestra_ldap.utils import apply_settings_to_legacy_config

__all__ = [
    "GeorchestraLdapClient",
    "LdapSettings",
    "LegacyConfigMissing",
    "LegacyScriptsMissing",
    "apply_settings_to_legacy_config",
    "role_exists",
    "org_exists",
    "get_org_users",
    "get_user_org",
    "get_user_infos",
    "get_role_infos",
    "get_user_roles",
    "get_role_users",
    "user_is_pending",
    "add_user_org",
]
