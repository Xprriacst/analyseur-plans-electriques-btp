# 📋 Fiche Projet — Analyseur Multi-Agent de Plans Électriques BTP

---

## 🎯 Objectif du Projet

Développer un système d'analyse automatisée de plans électriques BTP combinant **extraction de texte** et **analyse visuelle par IA** pour produire des rapports techniques détaillés destinés aux électriciens professionnels.

---

## 🏗️ Architecture Technique

### Stack Technologique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| **Orchestration workflow** | n8n | v3 |
| **Modèle IA** | Claude Opus | 4.6 |
| **Frontend** | HTML/CSS/JavaScript | Vanilla JS |
| **Format d'échange** | JSON + Base64 | - |
| **Communication** | Webhook HTTP | POST |

### Architecture Multi-Agent

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERFACE WEB HTML                        │
│  • Upload PDF + PNG (drag & drop)                           │
│  • URL Google Drive                                          │
│  • Configuration webhook dynamique                           │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP POST (JSON + Base64)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    WEBHOOK n8n                               │
│  • Réception multimodale (PDF + images)                     │
│  • Préparation des données binaires                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              EXTRACTION TEXTE PDF                            │
│  • Routing URL vs Base64                                     │
│  • Extract From File (n8n)                                   │
│  • Limitation 80 000 caractères                              │
└──────────────────────┬──────────────────────────────────────┘
                       │ Texte PDF + Images binaires
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          ORCHESTRATEUR (AI Agent Principal)                  │
│  • Claude Opus 4.6                                           │
│  • Passthrough Binary Images: ACTIVÉ                         │
│  • Coordination des 5 agents spécialisés                     │
│  • Synthèse finale multimodale                               │
└──────────────────────┬──────────────────────────────────────┘
                       │ Appels parallèles
        ┌──────────────┼──────────────┬──────────────┬─────────┐
        ▼              ▼              ▼              ▼         ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Agent 1    │ │   Agent 2    │ │   Agent 3    │ │   Agent 4    │ │   Agent 5    │
│              │ │              │ │              │ │              │ │              │
│ Infos        │ │ Courants     │ │ Courants     │ │ Sécurité     │ │ Automatismes │
│ Générales    │ │ Forts        │ │ Faibles      │ │ & Conformité │ │ & Domotique  │
│              │ │              │ │              │ │              │ │              │
│ • Texte seul │ │ • Texte      │ │ • Texte      │ │ • Texte      │ │ • Texte      │
│              │ │ • VISION     │ │ • VISION     │ │ • VISION     │ │ • VISION     │
│              │ │   (comptage) │ │   (symboles) │ │   (volumes)  │ │   (moteurs)  │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
        │              │              │              │              │
        └──────────────┴──────────────┴──────────────┴──────────────┘
                       │ Résultats agrégés
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              RAPPORT MARKDOWN FINAL                          │
│  • Structuré en 5 sections                                   │
│  • Tableaux quantitatifs                                     │
│  • Observations techniques                                   │
│  • Conformité réglementaire                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP Response
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              INTERFACE WEB (Affichage)                       │
│  • Rendu Markdown → HTML (marked.js)                        │
│  • Export PDF / Copie Markdown                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤖 Agents Spécialisés

### 1. **Agent Infos Générales** (Texte seul)
**Rôle** : Extraction des métadonnées administratives  
**Sources** : Cartouche, en-têtes, légendes (texte PDF)  
**Outputs** :
- Nom projet, adresse, maître d'ouvrage
- Date, échelle, indice de révision
- Type de bâtiment, surface, étages

### 2. **Agent Courants Forts** (Texte + Vision)
**Rôle** : Analyse des installations 230V/400V  
**Sources** : Texte PDF + **comptage visuel des symboles**  
**Outputs** :
- Tableaux électriques (TGBT, TD)
- Circuits par pièce (éclairage, prises)
- Comptage précis : prises 16A, points lumineux, interrupteurs
- Circuits spécialisés (32A, chauffage, VMC)
- Sections de câbles, protections
- Puissance totale installée

### 3. **Agent Courants Faibles** (Texte + Vision)
**Rôle** : Analyse VDI, réseau, sécurité  
**Sources** : Texte PDF + **identification visuelle symboles CF**  
**Outputs** :
- Prises RJ45 (Cat 6A), téléphone, TV
- Coffret de communication
- Détecteurs (mouvement, ouverture, fumée)
- Vidéosurveillance, interphone
- Topologie réseau

### 4. **Agent Sécurité & Conformité** (Texte + Vision)
**Rôle** : Vérification NFC 15-100 et réglementation ERP  
**Sources** : Texte PDF + **vérification visuelle emplacements**  
**Outputs** :
- Conformités détectées
- Points à vérifier sur site
- Non-conformités (avec articles NFC 15-100)
- Volumes de sécurité salle de bain
- Recommandations de mise en conformité

### 5. **Agent Automatismes & Domotique** (Texte + Vision)
**Rôle** : Identification des équipements motorisés et domotiques  
**Sources** : Texte PDF + **identification visuelle symboles automatismes**  
**Outputs** :
- Volets roulants, stores motorisés
- Détecteurs de présence, variateurs
- Thermostats, programmateurs
- Protocoles domotiques (KNX, Zigbee, Z-Wave)
- Scénarios d'automatisation

---

## 🎨 Interface Utilisateur

### Fonctionnalités

**Onglet 1 : Fichiers locaux**
- 📄 Upload PDF (drag & drop ou sélection)
- 🖼️ Upload images PNG (multi-upload)
- 👁️ Prévisualisation des fichiers
- ❌ Suppression individuelle

**Onglet 2 : URL Google Drive**
- 🔗 Saisie URL Google Drive
- 🔄 Conversion automatique en lien de téléchargement direct

**Configuration**
- ⚙️ URL webhook modifiable dynamiquement
- 💡 Aide contextuelle

**Affichage résultat**
- 📊 Rendu Markdown → HTML avec mise en forme
- 📋 Copie Markdown dans le presse-papiers
- ⬇️ Téléchargement fichier .md

---

## 📦 Fichiers Livrables

### Workflows n8n

| Fichier | Description | Statut |
|---------|-------------|--------|
| `workflow-v3-ultra.json` | **Version finale recommandée** — Passthrough Binary Images | ✅ Production |
| `workflow-v3-lite.json` | Version simplifiée avec 1 seul appel vision (test) | ✅ Test |
| `workflow-v3-vision.json` | Version avec 5 Basic LLM Chain vision (obsolète) | ⚠️ Archivé |
| `workflow-updated.json` | Version v2 avec prompts optimisés (sans vision) | ⚠️ Archivé |

### Frontend

| Fichier | Description |
|---------|-------------|
| `index.html` | Interface web complète (HTML/CSS/JS) |

### Documentation

| Fichier | Description |
|---------|-------------|
| `prompts-optimises.md` | Prompts système des 6 agents (optimisés Anthropic) |
| `FICHE_PROJET.md` | Ce document — fiche récapitulative |

### Scripts Python (développement)

| Fichier | Description |
|---------|-------------|
| `integrate_prompts.py` | Injection des prompts dans le workflow JSON |
| `generate_v3.py` | Génération workflow v3 avec vision (obsolète) |

---

## 🔑 Fonctionnalités Clés

### ✅ Analyse Multimodale
- **Texte** : Extraction PDF (légendes, cartouche, spécifications)
- **Vision** : Comptage symboles, identification emplacements, vérification volumes

### ✅ Architecture Simplifiée
- **Passthrough Binary Images** : Les images sont automatiquement transmises à tous les agents
- **Pas de pré-processing vision** : Les agents analysent directement avec leur capacité native
- **Flux linéaire** : Webhook → PDF Text → Orchestrateur → Agents → Rapport

### ✅ Spécialisation des Agents
- **5 domaines d'expertise** : Infos générales, CF, CFA, Sécurité, Automatismes
- **Prompts optimisés** : Structure XML, instructions explicites, format Markdown
- **Analyse parallèle** : Les 4 agents techniques travaillent simultanément

### ✅ Conformité Réglementaire
- **NFC 15-100** : Vérification sections, protections, volumes de sécurité
- **ERP** : SSI, BAES, compartimentage, accessibilité PMR
- **RE2020** : Efficacité énergétique, détection présence

### ✅ Interface Intuitive
- **Drag & drop** : Upload simplifié
- **Multi-source** : Fichiers locaux ou URL Google Drive
- **Configuration dynamique** : URL webhook modifiable
- **Export flexible** : Markdown, copie presse-papiers

---

## 🚀 Déploiement

### Prérequis

1. **n8n** installé et accessible
2. **Compte Anthropic** avec accès à Claude Opus 4.6
3. **Credentials n8n** configurés pour Anthropic API

### Configuration n8n

1. Importer `workflow-v3-ultra.json`
2. Configurer les credentials Anthropic :
   - ID : `VdlqaX9zUuo4smPu`
   - Nom : `Anthropic account`
3. Vérifier le webhook :
   - Path : `btp-electricite-agents`
   - Method : `POST`
   - Response Mode : `responseNode`
4. **Activer le workflow**

### Configuration Interface

1. Ouvrir `index.html` dans un navigateur
2. Configurer l'URL du webhook :
   - Format : `http://[serveur]:[port]/webhook-test/[path]`
   - Exemple : `http://187.77.169.67:5678/webhook-test/btp-electricite-agents-test`

### Test

1. Préparer un PDF de plan électrique
2. Préparer une image PNG du même plan
3. Uploader les deux fichiers dans l'interface
4. Lancer l'analyse
5. Vérifier le rapport généré (5 sections)

---

## 📊 Performances

### Temps d'exécution
- **Avec 1 agent** : ~30-60 secondes
- **Avec 5 agents** : ~2-5 minutes (appels parallèles)

### Coûts API (estimation Claude Opus 4.6)
- **Orchestrateur** : 1 appel (contexte texte + images)
- **Agent Infos Générales** : 1 appel (texte seul)
- **4 Agents techniques** : 4 appels (texte + vision)
- **Total** : ~6 appels par analyse

### Limites
- **Texte PDF** : 80 000 caractères max
- **Images** : Format PNG/JPEG, base64 encodé
- **Résolution images** : Recommandé 1920x1080 minimum pour comptage précis

---

## 🔄 Évolutions Possibles

### Court terme
- [ ] Support multi-pages PDF (conversion PDF → images)
- [ ] Export rapport en PDF formaté
- [ ] Historique des analyses
- [ ] Comparaison entre versions de plans

### Moyen terme
- [ ] Base de données des analyses
- [ ] API REST pour intégration externe
- [ ] Authentification utilisateurs
- [ ] Templates de rapports personnalisables

### Long terme
- [ ] Détection automatique des non-conformités critiques
- [ ] Génération de devis estimatifs
- [ ] Intégration BIM/CAO
- [ ] Module de formation (reconnaissance symboles)

---

## 📝 Notes Techniques

### Choix d'Architecture : Pourquoi Passthrough ?

**Option 1 (rejetée)** : Basic LLM Chain en amont
- ❌ Complexité : 5 nodes vision + merge
- ❌ Coût : 5 appels vision séparés
- ❌ Maintenance : Prompts dupliqués

**Option 2 (rejetée)** : Vision uniquement dans l'Orchestrateur
- ❌ Perte de spécialisation
- ❌ Agents ne voient pas les images

**Option 3 (adoptée)** : Passthrough Binary Images
- ✅ Simplicité : 1 paramètre à activer
- ✅ Efficacité : Vision native des agents
- ✅ Flexibilité : Chaque agent analyse selon ses besoins

### Optimisation des Prompts

**Principes appliqués** (Anthropic best practices) :
- Structure XML pour clarté (`<context>`, `<task>`, `<output_format>`)
- Instructions explicites et détaillées
- Exemples de format de sortie
- Gestion des cas limites
- Format Markdown pour lisibilité

---

## 👥 Cas d'Usage

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

## 📞 Support & Maintenance

### Logs & Debug
- Activer les logs n8n pour traçabilité
- Vérifier les erreurs dans la console navigateur
- Tester avec des plans simples d'abord

### Problèmes Courants

**"Failed to fetch"**
- Vérifier que n8n est accessible
- Vérifier l'URL du webhook
- Vérifier les CORS si domaine différent

**"Erreur d'extraction PDF"**
- Vérifier que le PDF n'est pas protégé
- Vérifier la taille du fichier (< 10 MB recommandé)

**"Analyse incomplète"**
- Vérifier que tous les agents sont connectés
- Vérifier les credentials Anthropic
- Vérifier les quotas API

---

## 🏆 Résultats

### Validation Technique
✅ **Passthrough Binary Images fonctionne** : Les agents reçoivent et analysent les images  
✅ **Comptage visuel précis** : Identification et quantification des symboles  
✅ **Analyse multimodale** : Croisement texte + vision réussi  
✅ **Architecture simplifiée** : Pas de nodes vision séparés nécessaires  

### Exemple de Résultat
**Plan testé** : Maison de Santé de Cellettes  
**Résultat** : Rapport de 6 pages avec :
- 25 locaux identifiés
- 21 unités PAC comptées
- 10 points ECS identifiés
- 7 types de luminaires catalogués
- Conformité NFC 15-100 vérifiée

---

## 📄 Licence & Crédits

**Développé avec** :
- n8n (workflow automation)
- Claude Opus 4.6 (Anthropic)
- Marked.js (Markdown rendering)

**Date de création** : Mars 2026  
**Version** : 3.0 Ultra (Passthrough)

---

*Fiche générée le 16 mars 2026*
