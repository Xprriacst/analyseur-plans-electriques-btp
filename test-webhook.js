const fs = require('fs');
const path = require('path');

const WEBHOOK_URL = process.argv[2] || 'http://187.77.169.67:5678/webhook/btp-electricite-agents-ultra-v4';
const TEST_MODE = process.argv[3] || 'plan_only'; // 'plan_only' or 'plan_dpgf'

const AAPC_DIR = path.join(__dirname, 'AAPC');

// Fichiers de test
const PDF_FILE = path.join(AAPC_DIR, 'PlanDCE-Lot10-Electricite-MSPCellettes.pdf');
const PNG_FILE = path.join(AAPC_DIR, 'PlanDCE-Lot10-Electricite-MSPCellettes.png');
const DPGF_FILE = path.join(AAPC_DIR, 'DPGF-Lot10-Electricite-MSPCellettes.xlsx');

console.log(`\n🔧 Test webhook: ${TEST_MODE}`);
console.log(`📡 URL: ${WEBHOOK_URL}\n`);

// Construire le payload
const payload = {};

// PDF en base64
if (fs.existsSync(PDF_FILE)) {
  payload.pdf_base64 = fs.readFileSync(PDF_FILE).toString('base64');
  payload.pdf_filename = 'PlanDCE-Lot10-Electricite.pdf';
  console.log(`✅ PDF chargé: ${(payload.pdf_base64.length / 1024 / 1024).toFixed(1)} MB (base64)`);
} else {
  console.log('❌ PDF non trouvé');
  process.exit(1);
}

// Image PNG en base64
if (fs.existsSync(PNG_FILE)) {
  const imgBase64 = fs.readFileSync(PNG_FILE).toString('base64');
  payload.images = [{
    base64: imgBase64,
    mime: 'image/png',
    filename: 'PlanDCE-Lot10-Electricite.png'
  }];
  console.log(`✅ Image chargée: ${(imgBase64.length / 1024).toFixed(0)} KB (base64)`);
} else {
  console.log('⚠️ Image PNG non trouvée, test sans image');
}

// DPGF Excel en base64 (si mode plan_dpgf)
if (TEST_MODE === 'plan_dpgf') {
  if (fs.existsSync(DPGF_FILE)) {
    payload.dpgf_base64 = fs.readFileSync(DPGF_FILE).toString('base64');
    payload.dpgf_filename = 'DPGF-Lot10-Electricite.xlsx';
    console.log(`✅ DPGF chargé: ${(payload.dpgf_base64.length / 1024).toFixed(0)} KB (base64)`);
  } else {
    console.log('❌ DPGF non trouvé');
    process.exit(1);
  }
} else {
  console.log('ℹ️  Mode plan seul (sans DPGF)');
}

const bodyStr = JSON.stringify(payload);
console.log(`\n📤 Envoi du payload: ${(bodyStr.length / 1024 / 1024).toFixed(1)} MB total`);
console.log('⏳ Attente de la réponse (peut prendre 1-5 minutes)...\n');

const startTime = Date.now();

fetch(WEBHOOK_URL, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: bodyStr,
  signal: AbortSignal.timeout(600000) // 10 min timeout
})
.then(async (res) => {
  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  console.log(`\n⏱️  Temps de réponse: ${elapsed}s`);
  console.log(`📊 Status: ${res.status} ${res.statusText}`);
  
  const text = await res.text();
  
  if (res.ok) {
    console.log(`\n✅ SUCCÈS!\n`);
    console.log('--- DÉBUT DU RAPPORT ---\n');
    console.log(text.substring(0, 3000));
    if (text.length > 3000) {
      console.log(`\n... [${text.length - 3000} caractères tronqués] ...`);
    }
    console.log('\n--- FIN DU RAPPORT ---');
    
    // Sauvegarder le rapport complet
    const outputFile = `test-result-${TEST_MODE}-${Date.now()}.md`;
    fs.writeFileSync(path.join(__dirname, outputFile), text);
    console.log(`\n💾 Rapport complet sauvegardé: ${outputFile}`);
  } else {
    console.log(`\n❌ ERREUR ${res.status}:`);
    console.log(text.substring(0, 2000));
  }
})
.catch((err) => {
  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  console.log(`\n❌ Erreur après ${elapsed}s:`);
  console.log(err.message);
});
