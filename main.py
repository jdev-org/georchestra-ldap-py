#!/usr/bin/env python3
import sys
import logging
from ldap3 import Server, Connection, ALL, SUBTREE
import config

# Logger vers fichier ldap-py.log
logging.basicConfig(
    filename="ldap-py.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger("ldap_lookup")


def search_user(conn, mail):
    filt = f"({config.LDAP_MAIL_ATTRIBUTE}={mail})"
    log.info(f"Filtre utilisateur : {filt}")

    conn.search(
        search_base=config.LDAP_SEARCH_BASE,
        search_filter=filt,
        search_scope=SUBTREE,
        attributes=["cn", "uid", "mail", "memberOf"]
    )
    return conn.entries


def extract_org_from_memberof(memberof):
    org_suffix = f"{config.LDAP_ORG_DN},{config.LDAP_SEARCH_BASE}"

    if not memberof:
        return None

    for entry in memberof:
        if entry.endswith(org_suffix):
            return entry.split(",")[0].split("=")[1]

    return None


def search_org_details(conn, org_cn):
    org_base = f"{config.LDAP_ORG_DN},{config.LDAP_SEARCH_BASE}"
    filt = f"(cn={org_cn})"

    conn.search(
        search_base=org_base,
        search_filter=filt,
        search_scope=SUBTREE,
        attributes=[
            "o", "cn", "mail", "businessCategory", "postalAddress",
            "orgUniqueId", "labeledURI", "description",
            "knowledgeInformation", "georchestraObjectIdentifier"
        ]
    )
    return conn.entries


def build_org_object(org_entry):
    """
    Construit un dictionnaire propre contenant toutes les infos d'organisation,
    même quand un champ est absent → valeur = None
    """
    keys = [
        "mail",
        "orgUniqueId",
        "georchestraObjectIdentifier",
        "postalAddress",
        "o",
        "labeledURI",
        "cn",
        "businessCategory",
        "description",
        "knowledgeInformation",
    ]

    result = {}

    for key in keys:
        result[key] = org_entry[key].value if key in org_entry else None

    return result


def search_roles(conn, user_dn):
    filt = f"(member={user_dn})"
    role_base = f"{config.LDAP_ROLE_DN},{config.LDAP_SEARCH_BASE}"

    conn.search(
        search_base=role_base,
        search_filter=filt,
        search_scope=SUBTREE,
        attributes=["cn"]
    )
    return conn.entries


def main():
    if len(sys.argv) < 2:
        log.error("Usage : python main.py <email>")
        sys.exit(1)

    target_mail = sys.argv[1]
    log.info(f"Recherche LDAP pour : {target_mail}")

    server = Server(
        config.LDAP_SERVER,
        port=config.LDAP_PORT,
        use_ssl=config.LDAP_USE_SSL,
        get_info=ALL
    )

    conn = Connection(
        server,
        user=config.LDAP_USER_DN,
        password=config.LDAP_PASSWORD,
        auto_bind=True
    )

    users = search_user(conn, target_mail)

    if not users:
        log.warning("Aucun utilisateur trouvé.")
        conn.unbind()
        return

    user = users[0]
    log.info(f"Utilisateur trouvé : {user.entry_dn}")

    # ---------------- ORGANISATION ----------------
    memberof_values = user.memberOf.values if "memberOf" in user else []
    org_cn = extract_org_from_memberof(memberof_values)

    org_object = None

    if org_cn:
        log.info(f"Organisation détectée via memberOf : {org_cn}")
        orgs = search_org_details(conn, org_cn)

        if orgs:
            org_entry = orgs[0]
            org_object = build_org_object(org_entry)

            log.info("Objet organisation construit :")
            for k, v in org_object.items():
                log.info(f"{k}: {v}")
        else:
            log.warning("Organisation non trouvée.")
    else:
        log.warning("Aucune organisation détectée dans memberOf.")

    # ---------------- ROLES ----------------
    role_entries = search_roles(conn, user.entry_dn)
    roles_list = [r.cn.value for r in role_entries] if role_entries else []

    log.info(f"Rôles détectés ({len(roles_list)}) : {roles_list}")

    conn.unbind()


if __name__ == "__main__":
    main()
