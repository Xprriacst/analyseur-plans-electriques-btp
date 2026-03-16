# 🔌 Analyseur Multi-Agent de Plans Électriques BTP

Application d'analyse automatisée de plans électriques BTP combinant **extraction de texte PDF** et **analyse visuelle par IA** pour produire des rapports techniques détaillés.

![Version](https://img.shields.io/badge/version-3.0_Ultra-blue)
![n8n](https://img.shields.io/badge/n8n-v3-orange)
![Claude](https://img.shields.io/badge/Claude-Opus_4.6-purple)

---

## 🎯 Fonctionnalités

- ✅ **Analyse multimodale** : Texte PDF + Vision IA
- ✅ **5 agents spécialisés** : Infos générales, Courants forts, Courants faibles, Sécurité, Automatismes
- ✅ **Comptage visuel** : Identification et quantification automatique des symboles électriques
- ✅ **Conformité NFC 15-100** : Vérification réglementaire automatisée
- ✅ **Interface intuitive** : Drag & drop, multi-source (fichiers locaux ou Google Drive)
- ✅ **Export Markdown** : Rapports structurés prêts à l'emploi

---

## 🏗️ Architecture

```
Interface Web → Webhook n8n → Extraction PDF → Orchestrateur IA
                                                      ↓
                                            (Passthrough Images)
                                                      ↓
                                    ┌─────────────────┴─────────────────┐
                                    ▼                                   ▼
                            5 Agents Spécialisés              Rapport Markdown
                            (Texte + Vision)
```

### Agents IA

| Agent | Rôle | Sources |
|-------|------|---------|
| **Infos Générales** | Métadonnées projet | Texte PDF |
| **Courants Forts** | Tableaux, circuits, prises | Texte + Vision |
| **Courants Faibles** | VDI, réseau, sécurité | Texte + Vision |
| **Sécurité** | Conformité NFC 15-100 | Texte + Vision |
| **Automatismes** | Domotique, motorisations | Texte + Vision |

---

## 🚀 Installation

### Prérequis

- **n8n** (version 3+)
- **Compte Anthropic** avec accès à Claude Opus 4.6
- **Navigateur web** moderne

### Configuration

1. **Importer le workflow dans n8n**
   ```bash
   # Importer workflow-v3-ultra.json dans n8n
   ```

2. **Configurer les credentials Anthropic**
   - Créer un credential "Anthropic account" dans n8n
   - Renseigner votre API key Anthropic

3. **Activer le workflow**
   - Vérifier le webhook path : `btp-electricite-agents`
   - Activer le workflow

4. **Ouvrir l'interface web**
   ```bash
   open index.html
   ```

5. **Configurer l'URL du webhook**
   - Dans l'interface, renseigner l'URL de votre instance n8n
   - Format : `http://[serveur]:[port]/webhook-test/btp-electricite-agents`

---

## 📖 Utilisation

### Upload de fichiers

1. **Onglet "Fichiers locaux"**
   - Glisser-déposer un PDF de plan électrique
   - Ajouter une ou plusieurs images PNG du plan
   - Cliquer sur "Analyser"

2. **Onglet "URL Google Drive"**
   - Coller l'URL d'un PDF sur Google Drive
   - Cliquer sur "Analyser"

### Résultat

Le rapport généré contient :
- 📋 Informations générales (projet, adresse, maître d'ouvrage...)
- ⚡ Courants forts (tableaux, circuits, comptage prises/luminaires)
- 📡 Courants faibles (réseau, sécurité, vidéosurveillance)
- 🛡️ Sécurité & conformité (NFC 15-100, volumes, protections)
- 🤖 Automatismes & domotique (volets, détecteurs, thermostats)

---

## 📁 Structure du Projet

```
windsurf-project-7/
├── workflow-v3-ultra.json    # Workflow n8n de production
├── index.html                 # Interface web
├── prompts-optimises.md       # Prompts système des agents
├── FICHE_PROJET.md           # Documentation complète
├── README.md                  # Ce fichier
├── .gitignore                # Fichiers ignorés par Git
└── archive/                   # Versions obsolètes
    ├── workflow-v3-lite.json
    ├── workflow-v3-vision.json
    └── workflow-updated.json
```

---

## 🔧 Technologies

| Composant | Technologie |
|-----------|-------------|
| Orchestration | n8n v3 |
| IA | Claude Opus 4.6 (Anthropic) |
| Frontend | HTML/CSS/JavaScript (Vanilla) |
| Markdown rendering | marked.js |
| Format d'échange | JSON + Base64 |

---

## 📊 Performances

- **Temps d'analyse** : 2-5 minutes (avec 5 agents)
- **Coût par analyse** : ~6 appels API Claude Opus 4.6
- **Précision comptage** : Dépend de la qualité des images (recommandé : 1920x1080 min)

---

## 🎓 Cas d'Usage

### Électriciens
- Chiffrage rapide des matériaux
- Vérification conformité avant intervention
- Détection des circuits manquants

### Bureaux d'Études
- Contrôle qualité des plans
- Génération de rapports techniques
- Validation réglementaire

### Maîtres d'Ouvrage
- Compréhension des installations
- Vérification des prestations
- Suivi de conformité

### Organismes de Contrôle
- Pré-contrôle Consuel
- Vérification accessibilité PMR
- Audit sécurité incendie

---

## 🔄 Roadmap

### Version actuelle : 3.0 Ultra
- ✅ Analyse multimodale (texte + vision)
- ✅ 5 agents spécialisés
- ✅ Passthrough Binary Images
- ✅ Interface web complète

### Prochaines versions
- [ ] Agent de comparaison DPGF (analyse des écarts quantitatifs)
- [ ] Support multi-pages PDF
- [ ] Export PDF formaté
- [ ] Historique des analyses
- [ ] API REST

---

## 📝 Licence

Projet développé en mars 2026.

---

## 🤝 Contribution

Pour toute question ou suggestion, ouvrir une issue sur GitHub.

---

## 📞 Support

Consulter la [documentation complète](FICHE_PROJET.md) pour plus de détails techniques.
