# Repository Overview *georchestra-ldap-py*

This repository contains a collection of Python scripts designed to easily manage users, roles, and organizations in a geOrchestra-compatible LDAP directory.  
The goal is to provide a simple, consistent, and automatable toolkit for administering LDAP without relying on heavy interfaces or manual commands.

## Prerequisites

- Python 3 installed (`python3` on most systems)
- Network access to the LDAP server and a bind account with write permissions
- A `config.py` file adjusted for your geOrchestra environment

## Quick setup

- (Optional) create a virtualenv: `python3 -m venv .venv && source .venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

## Configuration

All settings are in `config.py`:

- `LDAP_SERVER`, `LDAP_PORT`, `LDAP_USE_SSL`: LDAP target
- `LDAP_USER_DN`, `LDAP_PASSWORD`: bind account used by the scripts
- `LDAP_SEARCH_BASE`: suffix (e.g., `dc=georchestra,dc=org`)
- `LDAP_USERS_DN`, `LDAP_ORG_DN`, `LDAP_ROLE_DN`: relative DNs for users, orgs, and roles
- `LDAP_MAIL_ATTRIBUTE`: attribute used to look up a user by email

## Main Features

- **User creation** with the correct geOrchestra objectClasses  
- **Automatic assignment** of the `USER` role and the `C2C` organization
- **Account activation** (pending → users)
- **Role creation and assignment**
- **Organization creation**
- **Full retrieval** of user information
- **Targeted retrieval** of user roles
- **Clean user deletion** (removal from all groups)
- Modular architecture: all scripts share a common LDAP connection handler

## Purpose and usage

To make LDAP administration accessible and automatable by providing standalone, readable, composable scripts that remain fully compatible with geOrchestra, without requiring deep LDAP knowledge.

Each script can be used individually or integrated into CI/CD pipelines or internal automation tools.

# Using it as a Python library

The `ldap_actions` scripts remain untouched, but you can now reuse them through a thin Python API:

```python
from georchestra_ldap import GeorchestraLdapClient, LdapSettings

settings = LdapSettings.from_env()  # or LdapSettings(server="ldap://...", user_dn="...", password="...")
client = GeorchestraLdapClient(settings)

client.create_user("uid42", "uid42@example.org", "John", "Doe", "Secret123")
client.moderate_user("uid42@example.org")
client.add_user_role("uid42@example.org", "ADMIN")
client.read_user_roles("uid42@example.org")
```

Notes:
- `LdapSettings` reads the same environment variables as the legacy `config.py`.
- `GeorchestraLdapClient` applies those settings to the legacy config and calls the existing scripts directly (`create_user`, `create_role`, `delete_user`, etc.).
- The command-line usage remains unchanged; nothing is modified in `ldap_actions`.

## Practical examples (`examples/`)

- `examples/example_alice_flow.py`: ensures role `FOO` exists, checks/creates Alice in pending, then moderates her.
- `examples/example_roles_flow.py`: checks/creates + moderates Alice, reads her roles, adds `FOO` and `BAZ`, then removes `BAZ`.

## Configuration (environment variables)

All settings can be overridden without editing `config.py` by exporting the same variable names:
`LDAP_SERVER`, `LDAP_PORT`, `LDAP_USE_SSL`, `LDAP_USER_DN`, `LDAP_PASSWORD`,
`LDAP_USERS_DN`, `LDAP_PENDING_USERS_DN`, `LDAP_ORG_DN`, `LDAP_ROLE_DN`,
`LDAP_SEARCH_BASE`, `LDAP_MAIL_ATTRIBUTE`, `LDAP_DEFAULT_ROLE_CN`, `LDAP_DEFAULT_ORG_CN`.
`GeorchestraLdapClient` picks them up via `LdapSettings.from_env()` and applies them to the legacy scripts in-memory.

## Logging & debugging

The client uses the standard Python `logging` module. No logging is configured by default; enable it as needed:

```python
import logging
logging.basicConfig(level=logging.INFO)  # or DEBUG
```

Each client method logs the action name at INFO and will log a full traceback on exceptions. Password values are not logged.

# Summary of LDAP Scripts

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

# LDAP Command Summary Table

Run commands from the repository root (`python ldap_actions/<script>.py ...`).

| Action | Command |
|--------|---------|
| Read user information | `python ldap_actions/read_user_infos.py utest2@utest.fr` |
| Read user roles | `python ldap_actions/read_user_roles.py utest2@utest.fr` |
| Create a user (pending + USER + C2C) | `python ldap_actions/create_user.py utest2 utest2@utest.fr Test User2 MySecretPass123` |
| Activate a user (pending → users) | `python ldap_actions/moderate_user.py utest2@utest.fr` |
| Add a role to a user | `python ldap_actions/add_user_role.py utest2@utest.fr SUPERUSER` |
| Remove a role from a user | `python ldap_actions/remove_user_role.py utest2@utest.fr SUPERUSER` |
| Create a role if it does not exist | `python ldap_actions/create_role.py MYCUSTOMROLE "Optional description"` |
| Delete a role | `python ldap_actions/delete_role.py MYCUSTOMROLE` |
| Create an organization if it does not exist | `python ldap_actions/create_org.py MYORG "My Organization"` |
| Add a user to an organization (DN required) | `python ldap_actions/update_org_user.py "uid=utest2,ou=users,dc=georchestra,dc=org" MYORG` |
| Update last name (DN required) | `python ldap_actions/update_user_name.py "uid=utest2,ou=users,dc=georchestra,dc=org" NewLastname` |
| Delete a user | `python ldap_actions/delete_user.py utest2@utest.fr` |
