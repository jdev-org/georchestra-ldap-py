# Présentation du dépôt *georchestra-ldap-py*

Ce dépôt contient un ensemble de scripts Python permettant de gérer facilement les utilisateurs, rôles et organisations d’un annuaire LDAP compatible geOrchestra.  
L’objectif est de fournir une boîte à outils simple, cohérente et automatisable pour administrer un LDAP sans passer par des interfaces lourdes ou des commandes manuelles.

## Prérequis

- Python 3 installé (les scripts sont testés avec `python3`)
- Accès réseau au serveur LDAP et un compte disposant des droits d’écriture
- Fichier `config.py` renseigné pour votre environnement geOrchestra

## Installation rapide

- (Optionnel) créer un virtualenv : `python3 -m venv .venv && source .venv/bin/activate`
- Installer les dépendances : `pip install -r requirements.txt`

## Configuration

Les paramètres se trouvent dans `config.py` :

- `LDAP_SERVER`, `LDAP_PORT`, `LDAP_USE_SSL` : cible LDAP
- `LDAP_USER_DN`, `LDAP_PASSWORD` : compte utilisé pour les opérations
- `LDAP_SEARCH_BASE` : suffixe (ex: `dc=georchestra,dc=org`)
- `LDAP_USERS_DN`, `LDAP_ORG_DN`, `LDAP_ROLE_DN` : DNs relatifs aux unités d’utilisateurs, organisations et rôles
- `LDAP_MAIL_ATTRIBUTE` : attribut utilisé pour rechercher un utilisateur par email

## Fonctionnalités principales

- **Création d’utilisateurs** avec les objectClass geOrchestra corrects  
- **Ajout automatique** du rôle `USER` et de l’organisation `C2C`
- **Activation d’un compte** (pending → users)
- **Ajout et création de rôles**
- **Création d’organisations**
- **Lecture complète** des informations d’un utilisateur
- **Lecture ciblée des rôles**
- **Suppression propre** d’un utilisateur (nettoyage des groupes)
- Architecture modulaire : les scripts partagent un gestionnaire LDAP commun

## Objectif et usage

Rendre accessible et automatisable la gestion LDAP en fournissant des scripts autonomes, lisibles, composables et compatibles avec geOrchestra, sans nécessiter une connaissance avancée de LDAP.

Chaque script peut être utilisé individuellement ou intégré dans des pipelines CI/CD ou des outils internes.

# Utilisation comme bibliothèque Python

Les scripts de `ldap_actions` restent inchangés mais peuvent désormais être consommés depuis n’importe quel code Python grâce à une fine couche d’API :

```python
from georchestra_ldap import GeorchestraLdapClient, LdapSettings

settings = LdapSettings.from_env()  # ou LdapSettings(server="ldap://...", user_dn="...", password="...")
client = GeorchestraLdapClient(settings)

client.create_user("uid42", "uid42@example.org", "John", "Doe", "Secret123")
client.moderate_user("uid42@example.org")
client.add_user_role("uid42@example.org", "ADMIN")
client.read_user_roles("uid42@example.org")
```

Principes :
- `LdapSettings` lit la configuration existante (variables d’environnement identiques à `config.py`).
- `GeorchestraLdapClient` applique ces paramètres au `config.py` legacy puis appelle directement les fonctions des scripts (`create_user`, `create_role`, `delete_user`, etc.).
- Aucun changement n’est nécessaire dans `ldap_actions` : la CLI continue de fonctionner comme avant.

## Exemples pratiques (`examples/`)

- `examples/example_alice_flow.py` : crée le rôle `FOO`, vérifie/ crée Alice en pending puis la modère.
- `examples/example_roles_flow.py` : vérifie/ crée + modère Alice, lit ses rôles, assigne `FOO` et `BAZ`, retire `BAZ`.

## Configuration (variables d’environnement)

Toutes les variables sont surchargeables sans éditer `config.py` en exportant :
`LDAP_SERVER`, `LDAP_PORT`, `LDAP_USE_SSL`, `LDAP_USER_DN`, `LDAP_PASSWORD`,
`LDAP_USERS_DN`, `LDAP_PENDING_USERS_DN`, `LDAP_ORG_DN`, `LDAP_ROLE_DN`,
`LDAP_SEARCH_BASE`, `LDAP_MAIL_ATTRIBUTE`, `LDAP_DEFAULT_ROLE_CN`, `LDAP_DEFAULT_ORG_CN`.
`GeorchestraLdapClient` les lit via `LdapSettings.from_env()` et applique les valeurs au `config.py` legacy en mémoire.

## Logging et debug

Le client s’appuie sur le module standard `logging`. Rien n’est configuré par défaut ; active le logging selon tes besoins :

```python
import logging
logging.basicConfig(level=logging.INFO)  # ou DEBUG
```

Chaque méthode log le nom de l’action en INFO et produit un traceback complet en cas d’exception. Les mots de passe ne sont pas loggés.

# Synthèse des scripts LDAP

| Script | Fonction |
|--------|----------|
| **read_user_infos.py** | Recherche un utilisateur par email et affiche DN, uid, cn, mail, et tous les groupes (`memberOf`). |
| **read_user_roles.py** | Affiche uniquement les rôles LDAP d’un utilisateur (entrées situées sous `ou=roles`). |
| **create_user.py** | Crée un utilisateur dans `ou=pendingusers` avec les bons objectClass geOrchestra, génère un mot de passe SSHA, ajoute automatiquement le rôle `USER` et l’organisation `C2C`. |
| **moderate_user.py** | Active un utilisateur en le déplaçant de `ou=pendingusers` vers `ou=users` sans modifier rôles ni organisation. |
| **add_user_role.py** | Ajoute un rôle (groupe LDAP) à un utilisateur en insérant son DN dans l’attribut `member` du rôle. |
| **remove_user_role.py** | Retire un utilisateur d’un rôle existant. |
| **create_role.py** | Crée un nouveau rôle LDAP dans `ou=roles` si celui-ci n’existe pas déjà. |
| **delete_role.py** | Supprime un rôle après avoir retiré tous ses membres. |
| **create_org.py** | Crée une nouvelle organisation LDAP dans `ou=orgs` si elle n’existe pas. |
| **update_org_user.py** | Ajoute un utilisateur (DN) à une organisation donnée. |
| **update_user_name.py** | Met à jour le nom de famille (`sn`) d’un utilisateur via son DN. |
| **delete_user.py** | Supprime un utilisateur : le retire de tous ses rôles/organisations puis efface son entrée LDAP. |

# Tableau récapitulatif des commandes LDAP

Exécuter les commandes depuis la racine du dépôt (`python ldap_actions/<script>.py ...`).

| Action | Commande |
|--------|----------|
| Lire les informations d’un utilisateur | `python ldap_actions/read_user_infos.py utest2@utest.fr` |
| Lire les rôles d’un utilisateur | `python ldap_actions/read_user_roles.py utest2@utest.fr` |
| Créer un utilisateur (pending + USER + C2C) | `python ldap_actions/create_user.py utest2 utest2@utest.fr Test User2 MySecretPass123` |
| Activer un utilisateur (pending → users) | `python ldap_actions/moderate_user.py utest2@utest.fr` |
| Ajouter un rôle à un utilisateur | `python ldap_actions/add_user_role.py utest2@utest.fr SUPERUSER` |
| Retirer un rôle d’un utilisateur | `python ldap_actions/remove_user_role.py utest2@utest.fr SUPERUSER` |
| Créer un rôle si non existant | `python ldap_actions/create_role.py MYCUSTOMROLE "Description optionnelle"` |
| Supprimer un rôle | `python ldap_actions/delete_role.py MYCUSTOMROLE` |
| Créer une organisation si non existante | `python ldap_actions/create_org.py MYORG "My Organization"` |
| Ajouter un utilisateur à une organisation (DN requis) | `python ldap_actions/update_org_user.py "uid=utest2,ou=users,dc=georchestra,dc=org" MYORG` |
| Mettre à jour le nom de famille (DN requis) | `python ldap_actions/update_user_name.py "uid=utest2,ou=users,dc=georchestra,dc=org" NouveauNom` |
| Supprimer un utilisateur | `python ldap_actions/delete_user.py utest2@utest.fr` |
