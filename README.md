# 🩺 HA Diagnostic

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Release](https://img.shields.io/github/release/olivierguntern/HAdiagnostic.svg)](https://github.com/olivierguntern/HAdiagnostic/releases)

Add-on Home Assistant pour **diagnostiquer les erreurs** et les add-ons qui ne démarrent pas. Accessible directement depuis la barre latérale de Home Assistant.

---

## Fonctionnalités

- **Vue d'ensemble** : compteurs Total / OK / Arrêtés / En erreur
- **Détection automatique** des add-ons arrêtés anormalement ou en erreur
- **Analyse des logs** : extrait les messages d'erreur pertinents pour chaque add-on problématique
- **Interface intégrée** dans la barre latérale HA (ingress)
- **Bouton "Relancer"** pour refaire le diagnostic à la demande
- **Rapport JSON** exporté dans `/tmp/hadiagnostic_report.json`

---

## Installation

### Via HACS

1. Installez [HACS](https://hacs.xyz) si ce n'est pas déjà fait
2. Dans HACS → **Dépôts personnalisés** → ajoutez `https://github.com/olivierguntern/HAdiagnostic` (type : Add-on)
3. Installez **HA Diagnostic**

### Manuellement

1. Dans Home Assistant : **Paramètres → Add-ons → Boutique d'add-ons**
2. Cliquez les **3 points** ⋮ → **Dépôts**
3. Ajoutez : `https://github.com/olivierguntern/HAdiagnostic`
4. Cliquez **Ajouter** puis **Fermer**
5. Trouvez **HA Diagnostic** dans la boutique → **Installer**

---

## Configuration

Aucune configuration requise. L'add-on se connecte automatiquement à l'API Supervisor de Home Assistant.

---

## Utilisation

1. Après installation, allez dans l'onglet **Info** de l'add-on
2. Cochez **"Afficher dans la barre latérale"**
3. Cliquez **Démarrer**
4. Accédez à **HA Diagnostic** depuis le menu latéral

L'interface affiche :

```
┌─────────────────────────────────────┐
│  🩺 HA Diagnostic        [↻ Relancer]│
├──────┬──────┬──────────┬────────────┤
│  12  │  10  │    1     │     1      │
│ Total│  OK  │ Arrêtés  │ En erreur  │
├─────────────────────────────────────┤
│ ⚠ Mosquitto Broker                  │
│   → ERROR: port 1883 already in use │
│                                     │
│ ✗ MariaDB                           │
│   → CRITICAL: Cannot start mysqld   │
└─────────────────────────────────────┘
```

---

## Erreurs détectées

L'analyseur de logs détecte automatiquement :

| Pattern | Exemples |
|---------|----------|
| Niveaux d'erreur | `ERROR`, `CRITICAL`, `FATAL` |
| Échecs | `Failed`, `cannot`, `can't` |
| Exceptions Python | `Exception`, `Traceback` |
| Réseau | `connection refused`, `timeout` |
| Permissions | `permission denied`, `access denied` |
| Fichiers manquants | `not found`, `no such file` |
| Ports occupés | `address already in use` |

---

## Permissions requises

L'add-on nécessite `hassio_role: manager` pour lire les logs des autres add-ons via l'API Supervisor.

---

## Structure du projet

```
HAdiagnostic/
├── repository.yaml
├── LICENSE
└── hadiagnostic/
    ├── config.yaml
    ├── build.yaml
    ├── Dockerfile
    ├── icon.png
    ├── run.py
    ├── requirements.txt
    └── diagnostic/
        ├── supervisor_api.py
        ├── addon_checker.py
        └── log_parser.py
```

---

## Licence

MIT — voir [LICENSE](LICENSE)
