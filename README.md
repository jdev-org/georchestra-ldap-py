# Présentation du dépôt *ldap-py*

Ce dépôt contient un ensemble de scripts Python permettant de gérer facilement les utilisateurs, rôles et organisations d’un annuaire LDAP compatible geOrchestra.  
L’objectif est de fournir une boîte à outils simple, cohérente et automatisable pour administrer un LDAP sans passer par des interfaces lourdes ou des commandes manuelles.

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

## Objectif

Rendre accessible et automatisable la gestion LDAP en fournissant des scripts autonomes, lisibles, composables et compatibles avec geOrchestra, sans nécessiter une connaissance avancée de LDAP.

Chaque script peut être utilisé individuellement ou intégré dans des pipelines CI/CD ou des outils internes.

# Synthèse des scripts LDAP

| Script | Fonction |
|--------|----------|
| **read_user_infos.py** | Recherche un utilisateur par email et affiche ses informations : DN, uid, cn, mail, et tous les groupes (`memberOf`). |
| **read_user_roles.py** | Affiche uniquement les rôles LDAP d’un utilisateur (entrées situées dans `ou=roles`). |
| **create_user.py** | Crée un utilisateur dans `ou=pendingusers` avec les bons objectClass geOrchestra, génère un mot de passe SSHA, ajoute automatiquement le rôle `USER` et l’organisation `C2C`. |
| **moderate_user.py** | Active un utilisateur en le déplaçant de `ou=pendingusers` vers `ou=users` sans modifier ses rôles ni son organisation. |
| **add_user_role.py** | Ajoute un rôle (groupe LDAP) à un utilisateur en insérant son DN dans l’attribut `member` du rôle. |
| **create_role.py** | Crée un nouveau rôle LDAP dans `ou=roles` si celui-ci n’existe pas déjà. |
| **create_org.py** | Crée une nouvelle organisation LDAP dans `ou=orgs` si elle n’existe pas. |
| **delete_user.py** | Supprime un utilisateur : le retire de tous ses rôles + organisations puis efface son entrée LDAP. |


# Tableau récapitulatif des commandes LDAP

| Action | Commande |
|--------|----------|
| Lire les informations d’un utilisateur | `python ldap_actions/read_user_infos.py utest2@utest.fr` |
| Lire les rôles d’un utilisateur | `python ldap_actions/read_user_roles.py utest2@utest.fr` |
| Créer un utilisateur (pending + USER + C2C) | `python ldap_actions/create_user.py utest2 utest2@utest.fr Test User2 MySecretPass123` |
| Activer un utilisateur (pending → users) | `python ldap_actions/moderate_user.py utest2@utest.fr` |
| Ajouter un rôle à un utilisateur | `python ldap_actions/add_user_role.py "uid=utest2,ou=users,dc=georchestra,dc=org" SUPERUSER` |
| Créer un rôle si non existant | `python ldap_actions/create_role.py MYCUSTOMROLE` |
| Créer une organisation si non existante | `python ldap_actions/create_org.py MYORG "My Organization"` |
| Supprimer un utilisateur | `python ldap_actions/delete_user.py utest2@utest.fr` |


