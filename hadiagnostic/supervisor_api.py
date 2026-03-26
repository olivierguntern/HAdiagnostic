"""
Client pour l'API Supervisor Home Assistant.
Connexion via le token SUPERVISOR_TOKEN injecté automatiquement par HA.
"""

import os
import requests


SUPERVISOR_URL = "http://supervisor"


class SupervisorAPI:
    def __init__(self):
        self.token = os.environ.get("SUPERVISOR_TOKEN", "")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _get(self, endpoint: str) -> dict | None:
        try:
            response = requests.get(
                f"{SUPERVISOR_URL}{endpoint}",
                headers=self.headers,
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[API] Erreur lors de l'appel {endpoint} : {e}")
            return None

    def is_connected(self) -> bool:
        """Vérifie que la connexion à l'API Supervisor fonctionne."""
        result = self._get("/supervisor/ping")
        return result is not None and result.get("result") == "ok"

    def get_addons(self) -> list:
        """Retourne la liste de tous les add-ons installés."""
        result = self._get("/addons")
        if result and result.get("result") == "ok":
            return result.get("data", {}).get("addons", [])
        return []

    def get_addon_info(self, slug: str) -> dict | None:
        """Retourne les informations détaillées d'un add-on."""
        result = self._get(f"/addons/{slug}/info")
        if result and result.get("result") == "ok":
            return result.get("data", {})
        return None

    def get_addon_logs(self, slug: str) -> str:
        """Retourne les logs d'un add-on."""
        try:
            response = requests.get(
                f"{SUPERVISOR_URL}/addons/{slug}/logs",
                headers=self.headers,
                timeout=10,
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"[API] Impossible de récupérer les logs de {slug} : {e}")
            return ""
