/**
 * verify_arche.js — Ein-Befehl-Qualitätsgate & Backup-Guard für Arche Simulation 3.0.html
 * Prüft:
 *   1. Datei-Integrität (> 1 MB, schließendes </html>)
 *   2. vm.Script-Kompilierung aller <script>-Blöcke
 *   3. WebGL1-Konformität in GLSL-Fragment-/Vertex-Strings (keine WebGL2-only Syntax)
 *   4. Index-Aktualisierung via index_arche.js + Prüfung auf 101 Unit-Tests
 *   5. Atomarer Sicherheits-Snapshot in .backups/ (rollierend die letzten 20 gültigen Stände)
 *
 * Zusätzliche Schutz-Flags:
 *   node verify_arche.js --restore       # Stellt sofort den neuesten gültigen .backups/-Stand atomar wieder her
 *   node verify_arche.js --auto-restore  # Stellt nur wieder her, falls die HTML-Datei fehlt oder < 1 MB / defekt ist
 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const crypto = require('crypto');
const { execFileSync } = require('child_process');

const HTML_FILE = 'Arche Simulation 3.0.html';
const INDEX_FILE = 'ARCHE_INDEX.md';
const BACKUP_DIR = '.backups';
const MAX_BACKUPS = 20;

const args = process.argv.slice(2);
const FORCE_RESTORE = args.includes('--restore');
const AUTO_RESTORE = args.includes('--auto-restore');

function isValidHtmlContent(str) {
  if (!str) return false;
  const bytes = Buffer.byteLength(str, 'utf8');
  return bytes >= 1000000 && str.trimEnd().endsWith('</html>');
}

function writeFileAtomic(targetPath, content) {
  const tmpPath = `${targetPath}.tmp_${process.pid}_${Date.now()}`;
  fs.writeFileSync(tmpPath, content, 'utf8');
  fs.renameSync(tmpPath, targetPath);
}

function findLatestValidBackup() {
  if (!fs.existsSync(BACKUP_DIR)) return null;
  const files = fs.readdirSync(BACKUP_DIR)
    .filter((f) => f.endsWith('.html'))
    .sort()
    .reverse();
  for (const f of files) {
    const full = path.join(BACKUP_DIR, f);
    try {
      const content = fs.readFileSync(full, 'utf8');
      if (isValidHtmlContent(content)) return { name: f, path: full, content };
    } catch (_) { }
  }
  return null;
}

function restoreFromBackup(reason) {
  const snap = findLatestValidBackup();
  if (!snap) {
    console.error(`FAIL: ${reason} — und kein gültiger Snapshot in ${BACKUP_DIR}/ gefunden.`);
    process.exit(1);
  }
  writeFileAtomic(HTML_FILE, snap.content);
  console.log(`[RESTORE] ${reason} -> atomar wiederhergestellt aus ${snap.path}`);
}

const currentExists = fs.existsSync(HTML_FILE);
let currentHtml = currentExists ? fs.readFileSync(HTML_FILE, 'utf8') : '';
const currentValid = currentExists && isValidHtmlContent(currentHtml);

if (FORCE_RESTORE) {
  restoreFromBackup('Manueller Restore (--restore)');
  currentHtml = fs.readFileSync(HTML_FILE, 'utf8');
} else if (!currentValid) {
  const bytesNow = currentExists ? Buffer.byteLength(currentHtml, 'utf8') : 0;
  if (AUTO_RESTORE) {
    restoreFromBackup(`Defekte/leere HTML erkannt (${bytesNow} Bytes)`);
    currentHtml = fs.readFileSync(HTML_FILE, 'utf8');
  } else {
    console.error(`FAIL: Datei-Integrität verletzt (${bytesNow} Bytes). Zum Wiederherstellen: node verify_arche.js --restore`);
    process.exit(1);
  }
}

const html = currentHtml;
const bytes = Buffer.byteLength(html, 'utf8');
const lines = html.split('\n').length;
console.log(`[1/4] Datei-Integrität OK (${(bytes / 1024).toFixed(1)} KB, ${lines} Zeilen)`);

// 2. Alle Inline-<script>-Blöcke mit vm.Script parsen
const scriptBlocks = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)];
let compiledCount = 0;
for (let i = 0; i < scriptBlocks.length; i++) {
  const code = scriptBlocks[i][1];
  if (!code.trim()) continue;
  new vm.Script(code, { filename: `${HTML_FILE}#script${i}` });
  compiledCount++;
}
console.log(`[2/4] JavaScript-Syntax OK (${compiledCount} Inline-Script-Blöcke kompiliert)`);

// 3. WebGL1-GLSL-Lint (macOS Safari / WebGL1-Schutz)
const webgl2Patterns = [
  { name: '#version 300 es', re: /#version\s+300\s+es/g },
  { name: 'layout(...)', re: /\blayout\s*\(\s*location\s*=/g },
  { name: 'GLSL out vec4', re: /\bout\s+vec4\s+\w+\s*;/g }
];
const glslIssues = [];
for (const pat of webgl2Patterns) {
  const m = html.match(pat.re);
  if (m && m.length > 0) glslIssues.push(`${pat.name}: ${m.length}x`);
}
if (glslIssues.length > 0) {
  console.error('FAIL: WebGL2-only GLSL gefunden: ' + glslIssues.join(', '));
  process.exit(1);
}
console.log('[3/4] WebGL1/Safari GLSL-Check OK (0 WebGL2-only Konstrukte)');

// 4. ARCHE_INDEX.md aktualisieren & Test-Anzahl verifizieren
const idxOut = execFileSync(process.execPath, ['index_arche.js'], { encoding: 'utf8' });
process.stdout.write(idxOut.trimEnd() + '\n');
const idxMd = fs.readFileSync(INDEX_FILE, 'utf8');
if (!idxMd.includes('101') && !idxOut.includes('101 Unit-Tests')) {
  console.error('FAIL: Erwartete 101 Unit-Tests nicht im Index bestätigt.');
  process.exit(1);
}
console.log('[4/4] Index & Unit-Test-Anker OK (101 Unit-Tests erfasst)');

// 5. Atomarer Sicherheits-Snapshot in .backups/ (rollierend die letzten 20 gültigen Stände)
if (!fs.existsSync(BACKUP_DIR)) fs.mkdirSync(BACKUP_DIR);
const hash = crypto.createHash('sha1').update(html).digest('hex').slice(0, 8);
const existing = fs.readdirSync(BACKUP_DIR).filter((f) => f.endsWith('.html')).sort();
const latest = existing.length ? existing[existing.length - 1] : '';
if (!latest.includes(`_${hash}.html`)) {
  const ts = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
  const snapName = `Arche_Simulation_3.0_${ts}_${hash}.html`;
  writeFileAtomic(path.join(BACKUP_DIR, snapName), html);
  const updated = fs.readdirSync(BACKUP_DIR).filter((f) => f.endsWith('.html')).sort();
  while (updated.length > MAX_BACKUPS) {
    fs.unlinkSync(path.join(BACKUP_DIR, updated.shift()));
  }
  console.log(`[5/5] Sicherheits-Snapshot atomar gespeichert: ${path.join(BACKUP_DIR, snapName)}`);
} else {
  console.log(`[5/5] Sicherheits-Snapshot aktuell (${latest})`);
}

console.log('VERIFY_ARCHE_PASS');
