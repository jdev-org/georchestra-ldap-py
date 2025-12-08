# georchestra-ldap-py

Thin Python wrapper around the legacy `ldap_actions` scripts used with geOrchestra LDAP directories. Installable via pip, configurable via environment variables, and consumable as a small API.

## Quick install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
# or directly from git
# pip install "git+https://github.com/jdev-org/georchestra-ldap-py.git"
```

## Configure (env vars)

All settings are read via `LdapSettings.from_env()` and applied to the legacy `config.py` in memory. Override as needed:

```
LDAP_SERVER, LDAP_PORT, LDAP_USE_SSL,
LDAP_USER_DN, LDAP_PASSWORD,
LDAP_USERS_DN, LDAP_PENDING_USERS_DN, LDAP_ORG_DN, LDAP_ROLE_DN,
LDAP_SEARCH_BASE, LDAP_MAIL_ATTRIBUTE,
LDAP_DEFAULT_ROLE_CN, LDAP_DEFAULT_ORG_CN
```

## Example usage

```python
from georchestra_ldap import GeorchestraLdapClient, LdapSettings

client = GeorchestraLdapClient(LdapSettings.from_env())
client.create_role("FOO")
client.create_user("alice", "alice@example.org", "Alice", "Example", "Pwd123!")
client.moderate_user("alice@example.org")
client.add_user_role("alice@example.org", "FOO")
client.add_user_org("alice@example.org", "C2C")  # moves her out of other orgs first
client.read_user_roles("alice@example.org")
# custom settings example: see examples/custom_config.py
```

## Build & publish the docs (MkDocs Material)

- Build locally: `pip install mkdocs mkdocs-material mkdocstrings[python] && mkdocs build`
- Serve locally: `mkdocs serve` (opens on http://127.0.0.1:8000 by default)
- Publish to GitHub Pages (requires push rights): `mkdocs gh-deploy --force`
  - Or set up a GitHub Actions workflow (see `.github/workflows/docs.yml`) that builds the site and deploys to GitHub Pages. Configure Pages to use “GitHub Actions” as the source.


## Legacy scripts (CLI)

| Script | Function |
|--------|----------|
| **read_user_infos.py** | Searches for a user by email and displays information: DN, uid, cn, mail, and all groups (`memberOf`). |
| **read_user_roles.py** | Displays only the LDAP roles of a user (entries under `ou=roles`). |
| **create_user.py** | Creates a user in `ou=pendingusers` using proper geOrchestra objectClasses, generates an SSHA password, and automatically assigns the `USER` role and the `C2C` organization. |
| **moderate_user.py** | Activates a user by moving them from `ou=pendingusers` to `ou=users` without altering roles or organization. |
| **add_user_role.py** | Adds a role (LDAP group) to a user by inserting their DN into the role’s `member` attribute. |
| **remove_user_role.py** | Removes a user from an existing role. |
| **create_role.py** | Creates a new LDAP role in `ou=roles` if it does not already exist. |
| **delete_role.py** | Deletes a role after removing all its members. |
| **create_org.py** | Creates a new LDAP organization in `ou=orgs` if it does not already exist. |
| **update_org_user.py** | Adds a user (DN) to a given organization. |
| **update_user_name.py** | Updates the `sn` (last name) of a user via their DN. |
| **delete_user.py** | Deletes a user: removes them from all roles and organizations, then deletes the LDAP entry. |
| **role_exist.py** | Checks whether a role exists under `ou=roles`. |
| **get_user_infos.py** | Returns/prints a user entry by email (DN, uid, cn, mail, memberOf). |
| **get_role_infos.py** | Returns/prints a role entry by cn (DN, description, members). |
| **get_user_roles.py** | Returns/prints the role CNs for a user. |
| **get_user_org.py** | Returns/prints the organization CN for a user. |
| **user_is_pending.py** | Returns True if the user email is in pending users. |
| **org_exists.py** | Returns True if an organization exists under `ou=orgs`. |
| **add_user_org.py** | Adds a user (by email) to an organization, removing them from other orgs first. |
| **get_org_users.py** | Returns/prints the members (DNs) of an organization. |
| **get_role_users.py** | Returns/prints the members (DNs) of a role. |
