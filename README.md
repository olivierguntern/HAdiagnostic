# HA Diagnostic

Add-on Home Assistant pour diagnostiquer les erreurs et les add-ons qui ne démarrent pas.

## Fonctionnalités

- Liste tous les add-ons installés et leur état
- Détecte les add-ons arrêtés anormalement ou en erreur
- Analyse les logs pour extraire les messages d'erreur pertinents
- Exporte un rapport JSON complet dans `/tmp/hadiagnostic_report.json`

## Installation

1. Ajoutez ce repository dans Home Assistant :
   **Paramètres → Add-ons → Boutique d'add-ons → ⋮ → Dépôts**
   URL : `https://github.com/olivierguntern/HAdiagnostic`

2. Installez l'add-on **HA Diagnostic**

3. Lancez-le manuellement depuis l'onglet **Info**

## Utilisation

L'add-on se lance une seule fois (`startup: once`) et produit un rapport dans les logs :

```
=== HA Diagnostic v0.1.0 ===

[1/3] Récupération de la liste des add-ons...
      12 add-on(s) trouvé(s)

[2/3] Analyse de l'état des add-ons...

[3/3] Rapport de diagnostic

==================================================
⚠ Add-ons arrêtés (1) :
  - Mon Add-on (mon_addon)
    Dernières erreurs :
      → ERROR: Failed to bind port 8080: address already in use

✗ Add-ons en erreur (1) :
  - Autre Add-on (autre_addon) : error
    Dernières erreurs :
      → CRITICAL: Cannot connect to database
==================================================

Rapport complet exporté dans /tmp/hadiagnostic_report.json
```

## Structure du projet

```
HAdiagnostic/
├── config.yaml              # Configuration de l'add-on HA
├── Dockerfile               # Image Docker
├── run.py                   # Point d'entrée
├── requirements.txt         # Dépendances Python
└── hadiagnostic/
    ├── supervisor_api.py    # Client API Supervisor
    ├── addon_checker.py     # Vérification état des add-ons
    └── log_parser.py        # Analyse des logs
```

## Permissions requises

L'add-on nécessite `hassio_role: manager` pour accéder à l'API Supervisor et lire les logs des autres add-ons.
