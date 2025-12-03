class LegacyConfigMissing(RuntimeError):
    """Raised when ``config.py`` (used by ldap_actions scripts) is not importable."""


class LegacyScriptsMissing(RuntimeError):
    """Raised when the ``ldap_actions`` package cannot be imported."""
