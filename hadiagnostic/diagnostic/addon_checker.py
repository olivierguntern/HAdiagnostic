"""
Vérification de l'état des add-ons Home Assistant.
Identifie les add-ons arrêtés, en erreur ou qui ne démarrent pas.
"""

from hadiagnostic.supervisor_api import SupervisorAPI

# États considérés comme normaux
HEALTHY_STATES = {"started", "running"}

# États indiquant un problème
ERROR_STATES = {"error", "failed", "unknown"}

# États indiquant un arrêt (peut être normal ou anormal)
STOPPED_STATES = {"stopped"}


class AddonChecker:
    def __init__(self, api: SupervisorAPI):
        self.api = api

    def get_all_addons(self) -> list:
        """Récupère la liste complète des add-ons avec leurs infos."""
        addons_summary = self.api.get_addons()
        addons = []
        for addon in addons_summary:
            slug = addon.get("slug", "")
            info = self.api.get_addon_info(slug)
            if info:
                addons.append(info)
        return addons

    def check_addons(self, addons: list) -> dict:
        """
        Analyse l'état de chaque add-on et produit un rapport.

        Returns:
            dict avec les clés:
                - healthy: add-ons fonctionnels
                - stopped: add-ons arrêtés
                - errors: add-ons en erreur
                - total: nombre total d'add-ons
        """
        report = {
            "total": len(addons),
            "healthy": [],
            "stopped": [],
            "errors": [],
        }

        for addon in addons:
            state = addon.get("state", "unknown").lower()
            entry = {
                "name": addon.get("name", "Inconnu"),
                "slug": addon.get("slug", ""),
                "version": addon.get("version", "?"),
                "state": state,
            }

            if state in HEALTHY_STATES:
                report["healthy"].append(entry)
            elif state in ERROR_STATES:
                report["errors"].append(entry)
            elif state in STOPPED_STATES:
                # Vérifier si l'add-on devrait être démarré (boot: auto)
                boot = addon.get("boot", "manual")
                if boot == "auto":
                    report["stopped"].append(entry)
                else:
                    report["healthy"].append(entry)
            else:
                # État inconnu = potentiel problème
                report["errors"].append(entry)

        return report
