#!/usr/bin/env python3
"""
Génère le workflow n8n v3 avec :
- Routing input (URL / base64 PDF / images)
- Extraction texte PDF
- 5 Basic LLM Chain Vision spécialisés (avec Claude Opus + Image Binary)
- Merge des résultats texte + vision
- Orchestrateur + 5 agents texte
- Respond
"""
import json
import copy

# ─── Credentials ───
ANTHROPIC_CREDS = {"anthropicApi": {"id": "VdlqaX9zUuo4smPu", "name": "Anthropic account"}}
CLAUDE_MODEL = {
    "__rl": True,
    "value": "claude-opus-4-6",
    "mode": "list",
    "cachedResultName": "Claude Opus 4.6"
}

# ─── Vision prompts spécialisés ───
VISION_PROMPT_INFOS = """Analyse visuellement ce plan électrique BTP.

<task>
Extrais les informations générales visibles sur le plan :
- Cartouche (titre, adresse, date, échelle, indice de révision, bureau d'études)
- Orientation et disposition générale du bâtiment
- Nombre de pièces/zones visibles
- Étages représentés
- Légende générale si visible
</task>

<output_format>
Réponds en Markdown structuré avec un tableau des informations trouvées.
Mentionne ce qui est visible graphiquement mais absent du texte extrait.
</output_format>"""

VISION_PROMPT_CF = """Analyse visuellement ce plan électrique BTP pour identifier et COMPTER tous les symboles de courants forts.

<task>
Identifie et compte précisément chaque symbole graphique :
- Prises de courant 2P+T (symbole : demi-cercle avec traits)
- Prises 32A / spécialisées (symbole plus gros ou marqué)
- Points lumineux / plafonniers (symbole : cercle avec croix ou X)
- Appliques murales (symbole : demi-cercle sur mur)
- Spots encastrés (symbole : petit cercle plein)
- Interrupteurs simples (symbole : point avec trait)
- Interrupteurs va-et-vient (symbole : point avec 2 traits)
- Boutons poussoirs
- Tableaux électriques (rectangle avec symbole)
- Convecteurs / radiateurs
- Chauffe-eau (symbole ballon)
- VMC (symbole ventilateur)
- Boîtes de dérivation

Pour chaque pièce visible, compte les symboles séparément.
</task>

<output_format>
### Comptage par pièce
| Pièce | Prises 16A | Prises spé | Pts lumineux | Interrupteurs | Autres |
|-------|-----------|------------|-------------|---------------|--------|
| Cuisine | 6 | 2 (four, LV) | 2 | 1 SA + 1 VV | - |
| Salon | 5 | - | 3 | 2 VV | - |

### Totaux
| Symbole | Quantité totale |
|---------|----------------|
| Prises 16A | XX |
| Prises spécialisées | XX |
| Points lumineux | XX |
| Interrupteurs | XX |

### Observations visuelles
[Symboles non identifiés, zones floues, circuits visibles par couleur de trait]
</output_format>

<guidelines>
- Compte CHAQUE symbole individuellement, même groupés
- Distingue les symboles par pièce/zone
- Si un symbole est ambigu, mentionne-le dans les observations
- Indique la confiance du comptage (certain / approximatif)
</guidelines>"""

VISION_PROMPT_CF_FAIBLES = """Analyse visuellement ce plan électrique BTP pour identifier et COMPTER tous les symboles de courants faibles.

<task>
Identifie et compte précisément chaque symbole graphique :
- Prises RJ45 / réseau (symbole : carré avec RJ ou rectangle)
- Prises téléphone (symbole : T ou rectangle avec T)
- Prises TV / coaxiales (symbole : rectangle avec antenne)
- Coffret de communication / GTL
- Détecteurs de fumée DAAF (symbole : cercle avec DF ou fumée)
- Détecteurs de mouvement (symbole : œil ou secteur angulaire)
- Détecteurs d'ouverture (symbole : rectangle sur porte/fenêtre)
- Sirène (symbole : triangle ou haut-parleur)
- Centrale alarme
- Interphone / visiophone (symbole : combiné ou écran)
- Caméras (symbole : caméra stylisée)
- Haut-parleurs encastrés

Pour chaque pièce visible, compte les symboles séparément.
</task>

<output_format>
### Comptage par pièce
| Pièce | RJ45 | Téléphone | TV | DAAF | Détecteurs | Autres |
|-------|------|-----------|----|----- |-----------|--------|
| Salon | 2 | - | 1 | - | 1 PIR | - |
| Chambre 1 | 1 | - | 1 | 1 | - | - |

### Totaux
| Symbole | Quantité totale |
|---------|----------------|
| Prises RJ45 | XX |
| Prises TV | XX |
| DAAF | XX |
| Détecteurs mouvement | XX |

### Observations visuelles
[Symboles non identifiés, câblage visible, topologie réseau]
</output_format>

<guidelines>
- Les DAAF sont obligatoires : compte-les et signale si absents de certaines pièces
- Distingue RJ45 données des prises téléphone
- Identifie la topologie si les câbles sont dessinés (étoile depuis GTL)
</guidelines>"""

VISION_PROMPT_SECURITE = """Analyse visuellement ce plan électrique BTP pour identifier les éléments de sécurité électrique.

<task>
Identifie visuellement :
- Emplacement du/des tableau(x) électrique(s) (TGBT, divisionnaires)
- Symboles de mise à la terre (piquet de terre, liaison équipotentielle)
- Volumes de sécurité salle de bain (zones 0, 1, 2 si dessinées)
- Position des équipements par rapport aux points d'eau
- Prises ou appareils dans les volumes interdits
- DAAF (présence/absence par pièce)
- Coupure d'urgence (emplacement)
- Parafoudre (symbole au tableau)
- Cheminement des câbles si visible
- Schéma unifilaire si présent sur le plan
</task>

<output_format>
### Éléments de sécurité identifiés visuellement
| Élément | Présent | Emplacement | Observation |
|---------|---------|-------------|-------------|
| TGBT | Oui/Non | Garage | Accessible |
| Mise à la terre | Oui/Non | - | Symbole visible |
| Volumes SDB | Oui/Non | SDB | Zones tracées |
| DAAF chambres | Oui/Non | Ch1, Ch2 | Manquant Ch3 |

### Anomalies visuelles détectées
- [Prise dans volume 1 SDB visible à telle position]
- [Luminaire sans symbole IP dans SDB]

### Vérifications impossibles sur plan
- [Ce qui nécessite une visite sur site]
</output_format>

<guidelines>
- Concentre-toi sur ce qui est VISIBLE graphiquement
- Signale les anomalies de positionnement (prise trop près d'un point d'eau)
- Vérifie la présence des DAAF dans chaque chambre et couloir
</guidelines>"""

VISION_PROMPT_AUTOMATISMES = """Analyse visuellement ce plan électrique BTP pour identifier les symboles d'automatismes et domotique.

<task>
Identifie et compte précisément :
- Volets roulants (symbole : rectangle avec flèches haut/bas ou VR)
- Stores (symbole similaire aux volets)
- Commandes de volets (interrupteurs montée/descente)
- Commande centralisée volets
- Détecteurs de présence (symbole : secteur angulaire ou œil)
- Détecteurs crépusculaires
- Minuteries (symbole : horloge)
- Télérupteurs (symbole : T dans cercle)
- Variateurs (symbole : potentiomètre)
- Thermostat (symbole : thermomètre ou T°)
- Contacteur jour/nuit (symbole : horloge EDF)
- Motorisation portail (symbole : moteur sur portail)
- Porte de garage motorisée
- Symboles bus domotique (KNX, etc.)
</task>

<output_format>
### Comptage par pièce/zone
| Pièce/Zone | Volets | Détecteurs | Variateurs | Autres |
|------------|--------|-----------|-----------|--------|
| Salon | 2 VR | 1 présence | 1 | - |
| Entrée | - | 1 présence | - | Minuterie |
| Extérieur | - | 1 crépusculaire | - | Portail motorisé |

### Totaux
| Équipement | Quantité |
|-----------|----------|
| Volets roulants | XX |
| Détecteurs présence | XX |
| Variateurs | XX |
| Télérupteurs | XX |

### Observations visuelles
[Câblage spécifique visible, bus domotique, centralisation]
</output_format>

<guidelines>
- Distingue volets roulants des stores
- Identifie si les commandes sont individuelles ou centralisées
- Repère les symboles de bus domotique si présents
</guidelines>"""

# ─── Prompts système agents texte (repris du v2) ───
# On les charge depuis le v2
def load_v2_prompts():
    """Extract system prompts from v2 workflow"""
    with open("Analyseur Multi-Agent Électricité v2.json", "r", encoding="utf-8") as f:
        v2 = json.load(f)
    
    prompts = {}
    for node in v2["nodes"]:
        if "systemMessage" in node.get("parameters", {}).get("options", {}):
            prompts[node["name"]] = node["parameters"]["options"]["systemMessage"]
    return prompts

# ─── Updated orchestrator prompt ───
ORCHESTRATOR_SYSTEM = """Tu coordonnes l'analyse complète d'un plan électrique BTP en combinant DEUX sources de données :

<data_sources>
1. TEXTE PDF : texte extrait du plan (légendes, cartouche, notes techniques)
2. ANALYSE VISION : résultats du comptage visuel des symboles sur les images du plan (5 analyses spécialisées)
</data_sources>

<context>
Le rapport sera lu par des électriciens professionnels qui doivent chiffrer et réaliser l'installation.
Les données vision fournissent le COMPTAGE QUANTITATIF des symboles (prises, points lumineux, etc.).
Les données texte fournissent les SPÉCIFICATIONS TECHNIQUES (sections, protections, normes).
La combinaison des deux est essentielle pour un rapport complet.
</context>

<available_agents>
- agent_infos_generales : Extrait métadonnées projet depuis le texte
- agent_courants_forts : Analyse technique courants forts (texte + données vision CF)
- agent_courants_faibles : Analyse technique courants faibles (texte + données vision CF faibles)
- agent_securite : Vérifie conformité NFC 15-100 (texte + données vision sécurité)
- agent_automatismes : Identifie domotique (texte + données vision automatismes)
</available_agents>

<execution_strategy>
1. Appelle agent_infos_generales en premier
2. Appelle les 4 autres agents en parallèle
3. Synthétise en croisant les données texte ET vision
4. Si le comptage vision contredit le texte, signale l'écart
</execution_strategy>

<output_format>
# Rapport d'Analyse Électrique BTP

## 📋 Informations Générales
[Résultat agent_infos_generales]

## ⚡ Courants Forts
[Résultat agent_courants_forts — incluant les quantités issues de la vision]

## 📡 Courants Faibles
[Résultat agent_courants_faibles — incluant les quantités issues de la vision]

## 🛡️ Sécurité & Conformité
[Résultat agent_securite — incluant les anomalies visuelles]

## 🤖 Automatismes & Domotique
[Résultat agent_automatismes — incluant les quantités issues de la vision]

## 📊 Synthèse Globale
- Puissance totale estimée
- Cohérence texte/vision
- Points d'attention critiques
- Écarts détectés entre les sources
</output_format>

<guidelines>
- Conserve les tableaux des agents sans reformater
- Mets en évidence les données issues de la vision avec [VISION] si elles complètent le texte
- Signale tout écart entre comptage vision et spécifications texte
- Si aucune image n'a été fournie, précise que l'analyse est uniquement textuelle
</guidelines>"""


def make_node(id_, name, type_, version, pos, params=None, creds=None):
    node = {
        "parameters": params or {},
        "id": id_,
        "name": name,
        "type": type_,
        "typeVersion": version,
        "position": pos
    }
    if creds:
        node["credentials"] = creds
    return node


def make_llm_anthropic(id_, name, pos):
    return make_node(id_, name,
        "@n8n/n8n-nodes-langchain.lmChatAnthropic", 1.3, pos,
        params={"model": CLAUDE_MODEL, "options": {}},
        creds=ANTHROPIC_CREDS)


def make_vision_chain(id_, name, pos, system_prompt, text_prompt):
    """Create a Basic LLM Chain node configured for vision (image binary)"""
    return make_node(id_, name,
        "@n8n/n8n-nodes-langchain.chainLlm", 1.4, pos,
        params={
            "promptType": "define",
            "text": text_prompt,
            "messages": {
                "messageValues": [
                    {
                        "type": "system",
                        "message": system_prompt
                    },
                    {
                        "type": "user",
                        "messageType": "imageBinary",
                        "binaryImageDataKey": "image_0",
                        "imageDetail": "high"
                    }
                ]
            },
            "options": {}
        })


def build_workflow():
    nodes = []
    connections = {}

    def connect(src_name, dst_name, src_type="main", dst_type="main", src_idx=0, dst_idx=0):
        if src_name not in connections:
            connections[src_name] = {}
        if src_type not in connections[src_name]:
            connections[src_name][src_type] = [[]]
        # Extend outputs if needed
        while len(connections[src_name][src_type]) <= src_idx:
            connections[src_name][src_type].append([])
        connections[src_name][src_type][src_idx].append({
            "node": dst_name,
            "type": dst_type,
            "index": dst_idx
        })

    # ═══════════════════════════════════════════
    # 1. WEBHOOK
    # ═══════════════════════════════════════════
    nodes.append(make_node("webhook-main", "Webhook",
        "n8n-nodes-base.webhook", 2, [0, 600],
        params={
            "httpMethod": "POST",
            "path": "btp-electricite-agents",
            "responseMode": "responseNode",
            "options": {}
        }))

    # ═══════════════════════════════════════════
    # 2. CODE: PREPARE INPUT
    # Detects input type, prepares binary images, sets flags
    # ═══════════════════════════════════════════
    prepare_code = r"""
const body = $input.first().json.body || $input.first().json;
const item = {
  json: {
    has_pdf_url: !!body.pdf_url,
    has_pdf_base64: !!body.pdf_base64,
    has_images: !!(body.images && body.images.length > 0),
    pdf_url: body.pdf_url || '',
    pdf_base64: body.pdf_base64 || '',
    pdf_filename: body.pdf_filename || 'plan.pdf',
    image_count: body.images ? body.images.length : 0
  },
  binary: {}
};

// Convert base64 images to binary fields
if (body.images && body.images.length > 0) {
  for (let i = 0; i < body.images.length; i++) {
    item.binary['image_' + i] = {
      data: body.images[i].base64,
      mimeType: body.images[i].mime || 'image/png',
      fileName: body.images[i].filename || ('image_' + i + '.png')
    };
  }
}

// Convert base64 PDF to binary if present
if (body.pdf_base64) {
  item.binary['pdf_data'] = {
    data: body.pdf_base64,
    mimeType: 'application/pdf',
    fileName: body.pdf_filename || 'plan.pdf'
  };
}

return [item];
"""
    nodes.append(make_node("prepare-input", "Prepare Input",
        "n8n-nodes-base.code", 2, [280, 600],
        params={"jsCode": prepare_code, "mode": "runOnceForAllItems"}))
    connect("Webhook", "Prepare Input")

    # ═══════════════════════════════════════════
    # 3. SWITCH: Route by input type
    # Output 0: has pdf_url
    # Output 1: has pdf_base64
    # Output 2: has images (can be combined with 0 or 1)
    # ═══════════════════════════════════════════
    # We use IF nodes for cleaner routing

    # --- Text extraction path ---
    # IF has PDF URL
    nodes.append(make_node("if-has-url", "IF Has URL",
        "n8n-nodes-base.if", 2, [520, 400],
        params={
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                "conditions": [{
                    "id": "url-check",
                    "leftValue": "={{ $json.has_pdf_url }}",
                    "rightValue": True,
                    "operator": {"type": "boolean", "operation": "equals", "singleValue": True}
                }],
                "combinator": "and"
            }
        }))
    connect("Prepare Input", "IF Has URL")

    # Download PDF (URL path)
    nodes.append(make_node("download-pdf", "Download PDF",
        "n8n-nodes-base.httpRequest", 4.2, [760, 300],
        params={
            "url": "={{ (() => { const url = $json.pdf_url; const m = url.match(/\\/d\\/([a-zA-Z0-9_-]+)/); return m ? 'https://drive.google.com/uc?export=download&id=' + m[1] : url; })() }}",
            "options": {}
        }))
    connect("IF Has URL", "Download PDF", src_idx=0)  # true branch

    # Extract Text (URL path)
    nodes.append(make_node("extract-text-url", "Extract PDF Text",
        "n8n-nodes-base.extractFromFile", 1, [1000, 300],
        params={"operation": "pdf", "options": {}}))
    connect("Download PDF", "Extract PDF Text")

    # Set PDF Text (URL path)
    nodes.append(make_node("set-text-url", "Set PDF Text URL",
        "n8n-nodes-base.set", 3.4, [1240, 300],
        params={
            "assignments": {"assignments": [{
                "id": "pdf_text_url",
                "name": "pdf_text",
                "value": "={{ $json.text.substring(0, 80000) }}",
                "type": "string"
            }]},
            "options": {}
        }))
    connect("Extract PDF Text", "Set PDF Text URL")

    # --- Base64 PDF path (when no URL) ---
    # Extract Text from binary (base64 path) 
    nodes.append(make_node("extract-text-b64", "Extract PDF Base64",
        "n8n-nodes-base.extractFromFile", 1, [760, 520],
        params={"operation": "pdf", "options": {}, "binaryPropertyName": "pdf_data"}))
    connect("IF Has URL", "Extract PDF Base64", src_idx=1)  # false branch → check if base64

    nodes.append(make_node("set-text-b64", "Set PDF Text B64",
        "n8n-nodes-base.set", 3.4, [1000, 520],
        params={
            "assignments": {"assignments": [{
                "id": "pdf_text_b64",
                "name": "pdf_text",
                "value": "={{ $json.text ? $json.text.substring(0, 80000) : '' }}",
                "type": "string"
            }]},
            "options": {}
        }))
    connect("Extract PDF Base64", "Set PDF Text B64")

    # --- Merge text paths ---
    nodes.append(make_node("merge-text", "Merge Text",
        "n8n-nodes-base.merge", 3, [1480, 400],
        params={
            "mode": "append",
            "options": {}
        }))
    connect("Set PDF Text URL", "Merge Text", dst_idx=0)
    connect("Set PDF Text B64", "Merge Text", dst_idx=1)

    # ═══════════════════════════════════════════
    # 4. VISION BRANCH: 5 Basic LLM Chain nodes
    # ═══════════════════════════════════════════
    
    # IF has images
    nodes.append(make_node("if-has-images", "IF Has Images",
        "n8n-nodes-base.if", 2, [520, 900],
        params={
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                "conditions": [{
                    "id": "img-check",
                    "leftValue": "={{ $json.has_images }}",
                    "rightValue": True,
                    "operator": {"type": "boolean", "operation": "equals", "singleValue": True}
                }],
                "combinator": "and"
            }
        }))
    connect("Prepare Input", "IF Has Images")

    # 5 Vision chains + their LLMs
    vision_configs = [
        ("vision-infos", "Vision Infos Générales", [800, 700],
         VISION_PROMPT_INFOS, "Identifie les informations générales visibles sur ce plan électrique BTP."),
        ("vision-cf", "Vision Courants Forts", [800, 900],
         VISION_PROMPT_CF, "Compte et identifie tous les symboles de courants forts sur ce plan électrique BTP."),
        ("vision-cfaibles", "Vision Courants Faibles", [800, 1100],
         VISION_PROMPT_CF_FAIBLES, "Compte et identifie tous les symboles de courants faibles sur ce plan électrique BTP."),
        ("vision-securite", "Vision Sécurité", [800, 1300],
         VISION_PROMPT_SECURITE, "Identifie les éléments de sécurité électrique visibles sur ce plan BTP."),
        ("vision-auto", "Vision Automatismes", [800, 1500],
         VISION_PROMPT_AUTOMATISMES, "Compte et identifie tous les symboles d'automatismes et domotique sur ce plan BTP."),
    ]

    vision_chain_names = []
    for vid, vname, vpos, vsys, vtext in vision_configs:
        # Basic LLM Chain (vision)
        chain = make_vision_chain(vid, vname, vpos, vsys, vtext)
        nodes.append(chain)
        connect("IF Has Images", vname, src_idx=0)  # true branch
        
        # LLM for this chain
        llm_id = vid + "-llm"
        llm_name = "LLM " + vname
        llm_pos = [vpos[0], vpos[1] + 200]
        nodes.append(make_llm_anthropic(llm_id, llm_name, llm_pos))
        connect(llm_name, vname, src_type="ai_languageModel", dst_type="ai_languageModel")
        
        vision_chain_names.append(vname)

    # Code: Merge Vision Results
    merge_vision_code = r"""
// Collect all vision results from the 5 chains
const results = $input.all();
const sections = [];

for (const item of results) {
  if (item.json && item.json.text) {
    sections.push(item.json.text);
  } else if (item.json && item.json.response && item.json.response.text) {
    sections.push(item.json.response.text);
  } else if (typeof item.json === 'string') {
    sections.push(item.json);
  }
}

return [{
  json: {
    vision_analysis: sections.join('\n\n---\n\n') || 'Aucune analyse vision disponible.'
  }
}];
"""
    nodes.append(make_node("merge-vision", "Merge Vision Results",
        "n8n-nodes-base.code", 2, [1240, 1100],
        params={"jsCode": merge_vision_code, "mode": "runOnceForAllItems"}))
    
    for vname in vision_chain_names:
        connect(vname, "Merge Vision Results")

    # No images path: set empty vision
    nodes.append(make_node("no-vision", "No Vision",
        "n8n-nodes-base.set", 3.4, [1240, 1400],
        params={
            "assignments": {"assignments": [{
                "id": "no_vision",
                "name": "vision_analysis",
                "value": "Aucune image fournie — analyse uniquement textuelle.",
                "type": "string"
            }]},
            "options": {}
        }))
    connect("IF Has Images", "No Vision", src_idx=1)  # false branch

    # ═══════════════════════════════════════════
    # 5. MERGE ALL: text + vision
    # ═══════════════════════════════════════════
    nodes.append(make_node("merge-all", "Merge All",
        "n8n-nodes-base.merge", 3, [1700, 700],
        params={"mode": "combine", "combinationMode": "mergeByPosition"}))
    connect("Merge Text", "Merge All", dst_idx=0)
    connect("Merge Vision Results", "Merge All", dst_idx=1)

    # Also connect No Vision to merge
    nodes.append(make_node("merge-all-novision", "Merge All NoVision",
        "n8n-nodes-base.merge", 3, [1700, 1000],
        params={"mode": "combine", "combinationMode": "mergeByPosition"}))
    connect("Merge Text", "Merge All NoVision", dst_idx=0)
    connect("No Vision", "Merge All NoVision", dst_idx=1)

    # Code: Combine context
    combine_code = r"""
const items = $input.all();
let pdf_text = '';
let vision_analysis = '';

for (const item of items) {
  if (item.json.pdf_text) pdf_text = item.json.pdf_text;
  if (item.json.vision_analysis) vision_analysis = item.json.vision_analysis;
}

const combined = `=== DONNÉES TEXTE EXTRAITES DU PDF ===
${pdf_text}

=== ANALYSES VISION DES IMAGES DU PLAN ===
${vision_analysis}`;

return [{
  json: {
    pdf_text: pdf_text,
    vision_analysis: vision_analysis,
    combined_context: combined.substring(0, 120000)
  }
}];
"""
    nodes.append(make_node("combine-context", "Combine Context",
        "n8n-nodes-base.code", 2, [1960, 850],
        params={"jsCode": combine_code, "mode": "runOnceForAllItems"}))
    connect("Merge All", "Combine Context")
    connect("Merge All NoVision", "Combine Context")

    # ═══════════════════════════════════════════
    # 6. ORCHESTRATEUR + 5 AGENTS (from v2 but with updated prompt)
    # ═══════════════════════════════════════════
    
    # Load v2 prompts for agents
    try:
        v2_prompts = load_v2_prompts()
    except:
        v2_prompts = {}

    # Orchestrateur
    nodes.append(make_node("orchestrateur", "Orchestrateur",
        "@n8n/n8n-nodes-langchain.agent", 3.1, [2200, 850],
        params={
            "promptType": "define",
            "text": "={{ $json.combined_context }}",
            "options": {"maxIterations": 20},
            "systemMessage": ORCHESTRATOR_SYSTEM
        }))
    connect("Combine Context", "Orchestrateur")

    # LLM Orchestrateur
    nodes.append(make_llm_anthropic("llm-orch", "LLM Orchestrateur", [2100, 1080]))
    connect("LLM Orchestrateur", "Orchestrateur",
            src_type="ai_languageModel", dst_type="ai_languageModel")

    # 5 Agent tools + their LLMs
    agent_configs = [
        ("agent_infos_generales", "agent_infos_generales", [2200, 1120], "agent_infos_generales1"),
        ("agent_courants_forts", "agent_courants_forts", [2440, 1120], "agent_courants_forts1"),
        ("agent_courants_faibles", "agent_courants_faibles", [2680, 1120], "agent_courants_faibles1"),
        ("agent_securite", "agent_securite", [2920, 1120], "agent_securite1"),
        ("agent_automatismes", "agent_automatismes", [3160, 1120], "agent_automatismes1"),
    ]

    for aid, aname, apos, v2_name in agent_configs:
        sys_msg = v2_prompts.get(v2_name, "")
        
        nodes.append(make_node(aid, aname,
            "@n8n/n8n-nodes-langchain.agentTool", 3, apos,
            params={
                "text": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('Prompt__User_Message_', ``, 'string') }}",
                "options": {"systemMessage": sys_msg} if sys_msg else {}
            }))
        connect(aname, "Orchestrateur", src_type="ai_tool", dst_type="ai_tool")

        # LLM for agent
        llm_name = "LLM " + aname.replace("agent_", "").replace("_", " ").title()
        nodes.append(make_llm_anthropic(aid + "-llm", llm_name, [apos[0], apos[1] + 220]))
        connect(llm_name, aname, src_type="ai_languageModel", dst_type="ai_languageModel")

    # ═══════════════════════════════════════════
    # 7. RESPOND
    # ═══════════════════════════════════════════
    nodes.append(make_node("respond-webhook", "Respond to Webhook",
        "n8n-nodes-base.respondToWebhook", 1.1, [2460, 850],
        params={
            "respondWith": "text",
            "responseBody": "={{ $json.output }}",
            "options": {"responseCode": 200}
        }))
    connect("Orchestrateur", "Respond to Webhook")

    # ═══════════════════════════════════════════
    # BUILD FINAL WORKFLOW
    # ═══════════════════════════════════════════
    workflow = {
        "name": "BTP - Electricite Multi-Agent Analyzer v3 (Vision)",
        "nodes": nodes,
        "pinData": {},
        "connections": connections,
        "active": True,
        "settings": {
            "executionOrder": "v1",
            "callerPolicy": "workflowsFromSameOwner",
            "availableInMCP": False
        },
        "versionId": "v3-vision-2026",
        "meta": {
            "instanceId": "d83d6ee8c15e23092dde69cba9545217e1d643ea593a8410ee96a681c9fa9340"
        },
        "id": "stuCZVcJjwse49Xw",
        "tags": []
    }

    return workflow


if __name__ == "__main__":
    wf = build_workflow()
    
    with open("workflow-v3-vision.json", "w", encoding="utf-8") as f:
        json.dump(wf, f, indent=2, ensure_ascii=False)
    
    print("✅ Workflow v3 généré : workflow-v3-vision.json")
    print(f"   {len(wf['nodes'])} nodes")
    print(f"   {len(wf['connections'])} connections")
    print()
    print("Nodes:")
    for n in wf["nodes"]:
        print(f"  - {n['name']} ({n['type']})")
