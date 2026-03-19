#!/usr/bin/env python3
"""
Générateur de workflow n8n v4 avec agent DPGF
Ajoute un agent de comparaison DPGF au workflow v3-ultra
"""

import json

# Lire le prompt DPGF
with open('prompt-agent-dpgf.md', 'r', encoding='utf-8') as f:
    prompt_dpgf = f.read()

# Charger le workflow v3-ultra de base
with open('archive/workflow-v3-ultra-sans-dpgf.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# Modifier le nom
workflow['name'] = "BTP - Electricite Multi-Agent Analyzer v4 (avec DPGF)"
workflow['versionId'] = "v4-dpgf-2026"

# Modifier le node Prepare Input pour gérer le DPGF
prepare_input_code = """
const body = $input.first().json.body || $input.first().json;
const item = {
  json: {
    has_pdf_url: !!body.pdf_url,
    has_pdf_base64: !!body.pdf_base64,
    has_dpgf_base64: !!body.dpgf_base64,
    has_images: !!(body.images && body.images.length > 0),
    pdf_url: body.pdf_url || '',
    pdf_base64: body.pdf_base64 || '',
    dpgf_base64: body.dpgf_base64 || '',
    pdf_filename: body.pdf_filename || 'plan.pdf',
    dpgf_filename: body.dpgf_filename || 'dpgf.xlsx',
    image_count: body.images ? body.images.length : 0
  },
  binary: {}
};

if (body.images && body.images.length > 0) {
  for (let i = 0; i < body.images.length; i++) {
    item.binary['image_' + i] = {
      data: body.images[i].base64,
      mimeType: body.images[i].mime || 'image/png',
      fileName: body.images[i].filename || ('image_' + i + '.png')
    };
  }
}

if (body.pdf_base64) {
  item.binary['pdf_data'] = {
    data: body.pdf_base64,
    mimeType: 'application/pdf',
    fileName: body.pdf_filename || 'plan.pdf'
  };
}

if (body.dpgf_base64) {
  item.binary['dpgf_data'] = {
    data: body.dpgf_base64,
    mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    fileName: body.dpgf_filename || 'dpgf.xlsx'
  };
}

return [item];
"""

# Mettre à jour le code du node Prepare Input
for node in workflow['nodes']:
    if node['id'] == 'prepare-input':
        node['parameters']['jsCode'] = prepare_input_code

# Ajouter un node IF pour vérifier si DPGF est présent
if_has_dpgf_node = {
    "parameters": {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
            "conditions": [{
                "id": "dpgf-check",
                "leftValue": "={{ $json.has_dpgf_base64 }}",
                "rightValue": True,
                "operator": {"type": "boolean", "operation": "equals", "singleValue": True}
            }],
            "combinator": "and"
        },
        "options": {}
    },
    "id": "if-has-dpgf",
    "name": "IF Has DPGF Start",
    "type": "n8n-nodes-base.if",
    "typeVersion": 2,
    "position": [1344, 3840]
}

if_has_dpgf_after_plan_node = {
    "parameters": {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
            "conditions": [{
                "id": "dpgf-check-after-plan",
                "leftValue": "={{ $('Prepare Input').first().json.has_dpgf_base64 }}",
                "rightValue": True,
                "operator": {"type": "boolean", "operation": "equals", "singleValue": True}
            }],
            "combinator": "and"
        },
        "options": {}
    },
    "id": "if-has-dpgf-after-plan",
    "name": "IF Has DPGF After Plan",
    "type": "n8n-nodes-base.if",
    "typeVersion": 2,
    "position": [2864, 3600]
}

# Node d'extraction Excel DPGF (Extract From File)
extract_dpgf_node = {
    "parameters": {
        "operation": "xlsx",
        "binaryPropertyName": "dpgf_data",
        "options": {}
    },
    "id": "extract-dpgf",
    "name": "Extract DPGF Excel",
    "type": "n8n-nodes-base.extractFromFile",
    "typeVersion": 1,
    "position": [3104, 3488]
}

# Node pour convertir Excel en texte formaté
convert_dpgf_node = {
    "parameters": {
        "jsCode": """
// Convertir les données Excel en texte formaté pour l'IA
const data = $input.all();
let dpgfText = "DPGF - Décomposition du Prix Global et Forfaitaire\\n\\n";

for (const item of data) {
  const json = item.json;
  
  // Construire une ligne de tableau
  const row = Object.keys(json).map(key => {
    const value = json[key];
    return `${key}: ${value}`;
  }).join(' | ');
  
  dpgfText += row + '\\n';
}

return [{
  json: {
    dpgf_text: dpgfText.substring(0, 80000)
  }
}];
"""
    },
    "id": "convert-dpgf",
    "name": "Convert DPGF to Text",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [3344, 3488]
}

# Node Merge pour combiner le résultat de l'orchestrateur avec le DPGF
merge_with_dpgf_node = {
    "parameters": {
        "mode": "combine",
        "combinationMode": "mergeByPosition",
        "options": {}
    },
    "id": "merge-dpgf",
    "name": "Merge with DPGF",
    "type": "n8n-nodes-base.merge",
    "typeVersion": 3,
    "position": [3584, 3600]
}

# Agent DPGF
agent_dpgf_node = {
    "parameters": {
        "text": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('Prompt__User_Message_', `Analyse du plan:\n${$json.output}\n\nDPGF:\n${$json.dpgf_text}`, 'string') }}",
        "options": {
            "systemMessage": prompt_dpgf
        }
    },
    "id": "agent-dpgf",
    "name": "agent_dpgf_comparaison",
    "type": "@n8n/n8n-nodes-langchain.agentTool",
    "typeVersion": 3,
    "position": [3824, 3600]
}

# LLM pour l'agent DPGF
llm_dpgf_node = {
    "parameters": {
        "model": {"__rl": True, "value": "claude-opus-4-6", "mode": "list", "cachedResultName": "Claude Opus 4.6"},
        "options": {}
    },
    "id": "llm-dpgf",
    "name": "LLM DPGF",
    "type": "@n8n/n8n-nodes-langchain.lmChatAnthropic",
    "typeVersion": 1.3,
    "position": [3824, 3808],
    "credentials": {"anthropicApi": {"id": "VdlqaX9zUuo4smPu", "name": "Anthropic account"}}
}

# Node pour appeler directement l'agent DPGF (Basic LLM Chain)
call_dpgf_node = {
    "parameters": {
        "promptType": "define",
        "text": "=Analyse du plan:\n{{ $json.output }}\n\nDPGF:\n{{ $('Convert DPGF to Text').first().json.dpgf_text }}",
        "options": {},
        "systemMessage": prompt_dpgf
    },
    "id": "call-dpgf-analysis",
    "name": "Analyse DPGF",
    "type": "@n8n/n8n-nodes-langchain.chainLlm",
    "typeVersion": 1.5,
    "position": [3824, 3600]
}

# Node Set Final Output avec DPGF
set_final_dpgf_node = {
    "parameters": {
        "assignments": {
            "assignments": [{
                "id": "final_output",
                "name": "output",
                "value": "={{ $('Orchestrateur').first().json.output + '\n\n---\n\n# ANALYSE DPGF\n\n' + $json.text }}",
                "type": "string"
            }]
        },
        "options": {}
    },
    "id": "set-final-dpgf",
    "name": "Set Final Output DPGF",
    "type": "n8n-nodes-base.set",
    "typeVersion": 3.4,
    "position": [4064, 3600]
}

# Ajouter les nouveaux nodes
workflow['nodes'].extend([
    if_has_dpgf_node,
    if_has_dpgf_after_plan_node,
    extract_dpgf_node,
    convert_dpgf_node,
    merge_with_dpgf_node,
    call_dpgf_node,
    llm_dpgf_node,
    set_final_dpgf_node
])

# Modifier les connexions
# L'orchestrateur va maintenant vers IF Has DPGF au lieu de Respond to Webhook
workflow['connections']['Prepare Input'] = {
    "main": [[
        {"node": "IF Has URL", "type": "main", "index": 0},
        {"node": "IF Has DPGF Start", "type": "main", "index": 0}
    ]]
}

# IF Has DPGF : si oui -> Extract DPGF Excel
workflow['connections']['IF Has DPGF Start'] = {
    "main": [
        [{"node": "Extract DPGF Excel", "type": "main", "index": 0}],
        []
    ]
}

workflow['connections']['Orchestrateur'] = {
    "main": [[{"node": "IF Has DPGF After Plan", "type": "main", "index": 0}]]
}

workflow['connections']['IF Has DPGF After Plan'] = {
    "main": [
        [{"node": "Analyse DPGF", "type": "main", "index": 0}],
        [{"node": "Respond to Webhook", "type": "main", "index": 0}]
    ]
}

# Extract DPGF Excel -> Convert DPGF to Text
workflow['connections']['Extract DPGF Excel'] = {
    "main": [[{"node": "Convert DPGF to Text", "type": "main", "index": 0}]]
}

# Convert DPGF to Text: no downstream connection needed
# (accessed via $('Convert DPGF to Text') reference in Analyse DPGF)

# Analyse DPGF -> Set Final Output DPGF
workflow['connections']['Analyse DPGF'] = {
    "main": [[{"node": "Set Final Output DPGF", "type": "main", "index": 0}]]
}

# LLM DPGF -> Analyse DPGF
workflow['connections']['LLM DPGF'] = {
    "ai_languageModel": [[{"node": "Analyse DPGF", "type": "ai_languageModel", "index": 0}]]
}

# Set Final Output DPGF -> Respond to Webhook
workflow['connections']['Set Final Output DPGF'] = {
    "main": [[{"node": "Respond to Webhook", "type": "main", "index": 0}]]
}

# Sauvegarder le workflow v4
with open('workflow-v4-dpgf.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print("✅ Workflow v4 avec agent DPGF généré : workflow-v4-dpgf.json")
print("\nNouvelles fonctionnalités :")
print("- Upload optionnel d'un DPGF Excel")
print("- Extraction automatique des données DPGF")
print("- Agent de comparaison DPGF vs Plan")
print("- Tableau de synthèse des écarts quantitatifs")
print("- Calcul des métrés de câbles")
print("- Recommandations pour le chiffrage")
