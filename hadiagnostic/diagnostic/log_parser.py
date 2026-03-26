"""
Analyse des logs Home Assistant pour détecter les erreurs courantes.
"""

import re

# Patterns d'erreurs courants dans les logs HA / add-ons
ERROR_PATTERNS = [
    re.compile(r"\b(ERROR|CRITICAL|FATAL)\b", re.IGNORECASE),
    re.compile(r"\b(Failed|Failure|failed to|cannot|can't)\b", re.IGNORECASE),
    re.compile(r"\b(Exception|Traceback|raise)\b", re.IGNORECASE),
    re.compile(r"\b(connection refused|timeout|timed out)\b", re.IGNORECASE),
    re.compile(r"\b(permission denied|access denied)\b", re.IGNORECASE),
    re.compile(r"\b(not found|no such file|missing)\b", re.IGNORECASE),
    re.compile(r"\b(port.*in use|address already in use)\b", re.IGNORECASE),
]

# Patterns à ignorer (faux positifs courants)
IGNORE_PATTERNS = [
    re.compile(r"error_count: 0", re.IGNORECASE),
    re.compile(r"no errors", re.IGNORECASE),
]


class LogParser:
    def extract_errors(self, logs: str) -> list[str]:
        """
        Extrait les lignes d'erreur pertinentes depuis les logs.

        Args:
            logs: Contenu brut des logs (texte)

        Returns:
            Liste des lignes contenant des erreurs (dédupliquées)
        """
        if not logs:
            return []

        error_lines = []
        seen = set()

        for line in logs.splitlines():
            line = line.strip()
            if not line:
                continue

            # Ignorer les faux positifs
            if any(p.search(line) for p in IGNORE_PATTERNS):
                continue

            # Garder les lignes qui correspondent à un pattern d'erreur
            if any(p.search(line) for p in ERROR_PATTERNS):
                if line not in seen:
                    seen.add(line)
                    error_lines.append(line)

        return error_lines

    def summarize(self, logs: str) -> dict:
        """
        Retourne un résumé des erreurs trouvées dans les logs.

        Returns:
            dict avec 'count' et 'lines'
        """
        errors = self.extract_errors(logs)
        return {
            "count": len(errors),
            "lines": errors,
        }
