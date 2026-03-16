# Archive des versions obsolètes

Ces fichiers sont conservés pour référence historique mais ne sont plus utilisés en production.

## Workflows archivés
- **workflow-v3-lite.json** : Version de test avec 1 seul appel vision
- **workflow-v3-vision.json** : Version avec 5 Basic LLM Chain vision (architecture complexe)
- **workflow-updated.json** : Version v2 avec prompts optimisés (sans vision)

## Scripts de développement
- **integrate_prompts.py** : Script d'injection des prompts dans le workflow JSON
- **generate_v3.py** : Script de génération du workflow v3 avec vision

## Workflow de production
Le workflow actuel en production est **workflow-v3-ultra.json** (architecture Passthrough Binary Images).

