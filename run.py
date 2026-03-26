#!/usr/bin/env python3
"""
HA Diagnostic - Point d'entrée principal
Diagnostique les add-ons Home Assistant et détecte les erreurs.
"""

import json
import sys
from hadiagnostic.addon_checker import AddonChecker
from hadiagnostic.log_parser import LogParser
from hadiagnostic.supervisor_api import SupervisorAPI


def main():
    print("=== HA Diagnostic v0.1.0 ===\n")

    api = SupervisorAPI()

    # Vérifier la connexion à l'API Supervisor
    if not api.is_connected():
        print("[ERREUR] Impossible de se connecter à l'API Supervisor.")
        print("Vérifiez que l'add-on a bien 'hassio_api: true' dans config.yaml")
        sys.exit(1)

    checker = AddonChecker(api)
    parser = LogParser()

    # Récupérer tous les add-ons
    print("[1/3] Récupération de la liste des add-ons...")
    addons = checker.get_all_addons()
    print(f"      {len(addons)} add-on(s) trouvé(s)\n")

    # Analyser l'état de chaque add-on
    print("[2/3] Analyse de l'état des add-ons...")
    report = checker.check_addons(addons)

    # Afficher le résumé
    print("\n[3/3] Rapport de diagnostic\n")
    print("=" * 50)

    if not report["errors"] and not report["stopped"]:
        print("✓ Tous les add-ons fonctionnent correctement.")
    else:
        if report["stopped"]:
            print(f"\n⚠ Add-ons arrêtés ({len(report['stopped'])}) :")
            for addon in report["stopped"]:
                print(f"  - {addon['name']} ({addon['slug']})")
                logs = api.get_addon_logs(addon["slug"])
                errors = parser.extract_errors(logs)
                if errors:
                    print(f"    Dernières erreurs :")
                    for err in errors[-3:]:
                        print(f"      → {err}")

        if report["errors"]:
            print(f"\n✗ Add-ons en erreur ({len(report['errors'])}) :")
            for addon in report["errors"]:
                print(f"  - {addon['name']} ({addon['slug']}) : {addon['state']}")
                logs = api.get_addon_logs(addon["slug"])
                errors = parser.extract_errors(logs)
                if errors:
                    print(f"    Dernières erreurs :")
                    for err in errors[-3:]:
                        print(f"      → {err}")

    print("\n" + "=" * 50)

    # Exporter le rapport JSON
    with open("/tmp/hadiagnostic_report.json", "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("\nRapport complet exporté dans /tmp/hadiagnostic_report.json")


if __name__ == "__main__":
    main()
