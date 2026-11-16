/**
 * index_arche.js
 * Automatischer Struktur- und Zeilennummern-Index für Arche Simulation 3.0 (arche_2_0.html)
 * Generiert die Datei ARCHE_INDEX.md im Projektordner.
 *
 * Goldene Arbeitsregel:
 * Vor jedem Code-Edit ARCHE_INDEX.md lesen und nach dem Edit "node index_arche.js" ausführen!
 */

const fs = require('fs');
const path = require('path');

const projectDir = __dirname;
const allFiles = fs.readdirSync(projectDir);

// Finde die Haupt-HTML-Datei
let targetFile = allFiles.find(f => f.toLowerCase() === 'arche simulation 3.0.html') ||
                 allFiles.find(f => f.toLowerCase() === 'arche_2_0.html') ||
                 allFiles.find(f => f.toLowerCase().endsWith('.html') && f.toLowerCase().includes('arche')) ||
                 allFiles.find(f => f.toLowerCase().endsWith('.html'));

if (!targetFile) {
  console.error('[index_arche] Keine HTML-Datei im Verzeichnis gefunden:', projectDir);
  process.exit(1);
}

const targetPath = path.join(projectDir, targetFile);
const stat = fs.statSync(targetPath);
const fileSizeKB = (stat.size / 1024).toFixed(1);
const content = fs.readFileSync(targetPath, 'utf8');
const lines = content.split(/\r?\n/);
const totalLines = lines.length;

console.log(`[index_arche] Analysiere ${targetFile} (${totalLines} Zeilen, ${fileSizeKB} KB)...`);

// 1. Hilfsfunktion zum Parsen von String-Literalen mit Berücksichtigung von Escaping
function parseStringLiteral(str) {
  if (!str) return null;
  const quote = str[0];
  if (quote !== "'" && quote !== '"') return null;
  let val = '';
  let i = 1;
  while (i < str.length) {
    const ch = str[i];
    if (ch === '\\') {
      val += str[i + 1] || '';
      i += 2;
    } else if (ch === quote) {
      return { value: val, endIndex: i };
    } else {
      val += ch;
      i++;
    }
  }
  return null;
}

// Datenstrukturen
const docSections = [];
const banners = [];
const namespaces = [];
const functionsByModule = {
  'Arche.Procedural': [],
  'Arche.Materials': [],
  'Arche.Assets': [],
  'Arche.Environment': [],
  'Arche.Fauna': [],
  'Arche.Physics': [],
  'Arche.Performance': [],
  'Arche.UI': [],
  'Arche.Player': [],
  'Top-Level & Simulation Core': []
};
const shipyardAssemblies = [];
const araratAssemblies = [];
const unitTests = [];

// Zonen-Flags
let inShipyard = false;
let inArarat = false;
let shipyardStart = 0, shipyardEnd = 0;
let araratStart = 0, araratEnd = 0;

for (let i = 0; i < totalLines; i++) {
  const lineNum = i + 1;
  const rawLine = lines[i];
  const tr = rawLine.trim();

  // --- A. Haupt-Sektionen (HTML / CSS / JS) ---
  if (/<style/i.test(tr)) {
    docSections.push({ line: lineNum, tag: '<style>', desc: 'CSS-Stylesheets & UI-Design' });
  } else if (/<\/style>/i.test(tr)) {
    docSections.push({ line: lineNum, tag: '</style>', desc: 'Ende CSS-Stylesheets' });
  } else if (/<body/i.test(tr)) {
    docSections.push({ line: lineNum, tag: '<body...>', desc: 'DOM-Hierarchie, HUD-Container & Canvas' });
  } else if (/<\/body>/i.test(tr)) {
    docSections.push({ line: lineNum, tag: '</body>', desc: 'Ende DOM-Hierarchie' });
  } else if (/<script/i.test(tr)) {
    docSections.push({ line: lineNum, tag: '<script>', desc: 'Beginn Haupt-JavaScript (Three.js & Arche Engine)' });
  } else if (/<\/script>/i.test(tr)) {
    docSections.push({ line: lineNum, tag: '</script>', desc: 'Ende Haupt-JavaScript' });
  }

  // --- B. Große Architektur-Banner (Kommentar-Trennblöcke) ---
  if (tr.includes('// ===') && i + 1 < totalLines && lines[i + 1].trim().startsWith('//')) {
    const titleLine = lines[i + 1].trim().replace(/^\/\/\s*/, '').trim();
    if (titleLine.length > 3 && !titleLine.startsWith('===') && titleLine.length < 90) {
      banners.push({ line: lineNum + 1, title: titleLine });
    }
  }

  // --- C. Arche.* Namespaces & Registry Initialisierungen ---
  if (/^(?:window\.)?Arche\s*=\s*\{/.test(tr)) {
    namespaces.push({ line: lineNum, name: 'window.Arche', desc: 'Arche Root-Namespace & State/Config/Kinematik-Arrays' });
  } else if (/^Arche\.Config\s*=\s*/.test(tr) || /^\s*Config:\s*\{/.test(tr) && lineNum < 1840) {
    namespaces.push({ line: lineNum, name: 'Arche.Config', desc: 'Biblische Ellen-Geometrie, EN 338 & Streifen-Konfiguration' });
  } else if (/^Arche\.State\s*=\s*/.test(tr) || /^\s*State:\s*\{/.test(tr) && lineNum < 1840) {
    namespaces.push({ line: lineNum, name: 'Arche.State', desc: 'Laufzeit-Zustand, Kinematik (kin), Streifen-Arrays & Modus' });
  } else if (/^Arche\.UI\.dom\s*=\s*/.test(tr) || /^\s*UI:\s*\{/.test(tr) && lineNum < 1870) {
    namespaces.push({ line: lineNum, name: 'Arche.UI', desc: 'UI-DOM-Bindings, Bilinguale Tooltips (DE/EN) & Viewport-Sync' });
  } else if (/^Arche\.I18n\s*=\s*\{/.test(tr)) {
    namespaces.push({ line: lineNum, name: 'Arche.I18n', desc: 'Bilinguale Sprach-Engine (DE/EN), GUI-Labels & Option-Maps' });
  } else if (/^Arche\.Procedural\s*=\s*\{/.test(tr) || /^\s*Procedural:\s*\{/.test(tr) && lineNum < 1870) {
    namespaces.push({ line: lineNum, name: 'Arche.Procedural', desc: 'Prozedurale Texturen, Normal-Maps, PBR-POM-Shader & Shader-Kompilierung' });
  } else if (/^Arche\.Groups\s*=\s*\{/.test(tr)) {
    namespaces.push({ line: lineNum, name: 'Arche.Groups', desc: 'Three.js Szenengruppen-Registry (hullGroup, interiorGroup, shipyardGroup, etc.)' });
  } else if (/^Arche\.Materials\s*=\s*\{/.test(tr)) {
    namespaces.push({ line: lineNum, name: 'Arche.Materials', desc: 'Material-Registry (Gopherholz, Eiche, Zypresse, Bronze, Wasser, etc.)' });
  } else if (/^Arche\.Assets\s*=\s*\{/.test(tr) || /^\s*Assets:\s*\{/.test(tr) && lineNum < 1870) {
    namespaces.push({ line: lineNum, name: 'Arche.Assets', desc: 'Blender-.glb-Asset-Pipeline (GLTFLoader, Z-Up, Replace-Targets, Thermik/Slice-Shader)' });
  } else if (/^Arche\.Fauna\s*=\s*\{/.test(tr) || /^\s*Fauna:\s*\{/.test(tr) && lineNum < 1870) {
    namespaces.push({ line: lineNum, name: 'Arche.Fauna', desc: '3D-Fauna-Engine: Loft-Geometrien, Tier-Archetypen, Zugochsen & Knechte' });
  } else if (/^Arche\.Environment\s*=\s*\{/.test(tr) || /^\s*Environment:\s*\{/.test(tr) && lineNum < 1870) {
    namespaces.push({ line: lineNum, name: 'Arche.Environment', desc: 'Werftplatz (buildShipyard3D), Ararat-Massiv (buildAraratLandingSite3D), Botanik' });
  } else if (/^Arche\.Physics\s*=\s*\{/.test(tr) || /^\s*Physics:\s*\{/.test(tr) && lineNum < 1870) {
    namespaces.push({ line: lineNum, name: 'Arche.Physics', desc: 'Physik-Engine: Ozeanwellen, Göpel-Schichtplan, Mikroklima, D\'Alembert, Norris' });
  } else if (/^Arche\.Performance\s*=\s*/.test(tr)) {
    namespaces.push({ line: lineNum, name: 'Arche.Performance', desc: 'Auto-FPS-Governor (Tier 1-4 Quality-Manager) & Instanz-Reduktion' });
  } else if (/^Arche\.Player\s*=\s*\{/.test(tr) || /^\s*Player:\s*\{/.test(tr) && lineNum < 1870) {
    namespaces.push({ line: lineNum, name: 'Arche.Player', desc: 'Kamera-Steuerung (WASD/Orbit), First-Person & 3D-HUD-Labels' });
  }

  // --- D. 3D-Baugruppen Zonen-Erkennung ---
  if (/buildShipyard3D\s*=\s*function/i.test(tr)) {
    inShipyard = true;
    shipyardStart = lineNum;
  }
  if (inShipyard && (/buildAraratLandingSite3D\s*=\s*function/i.test(tr) || /Arche\.Environment\.updateLandmarks/i.test(tr))) {
    inShipyard = false;
    shipyardEnd = lineNum - 1;
  }

  if (/buildAraratLandingSite3D\s*=\s*function/i.test(tr)) {
    inArarat = true;
    araratStart = lineNum;
  }
  if (inArarat && /updateLandmarksAndTerrain3D\s*=\s*function/i.test(tr)) {
    inArarat = false;
    araratEnd = lineNum - 1;
  }

  // Baugruppen im Werftplatz
  if (inShipyard) {
    const syUserData = tr.match(/shipyardGroup\.userData\.([A-Za-z0-9_]+)\s*=\s*(.+);?/);
    const syBanner = tr.match(/^\/\/\s*(BAUGRUPPE\s+[0-9]+:[^=]+)/);
    const syComment = tr.match(/^\/\/\s*([0-9]+\.\s+[A-ZÄÖÜa-zäöü].+)/);
    if (syBanner) {
      shipyardAssemblies.push({ line: lineNum, type: 'Kapitel 13 Baugruppe', name: syBanner[1].trim(), code: '' });
    } else if (syUserData) {
      shipyardAssemblies.push({ line: lineNum, type: 'userData', name: `shipyardGroup.userData.${syUserData[1]}`, code: syUserData[2].substring(0, 65) });
    } else if (syComment && !tr.includes('===') && !syComment[1].includes('Primärast') && !syComment[1].includes('horizontale')) {
      shipyardAssemblies.push({ line: lineNum, type: 'Abschnitt', name: syComment[1].trim(), code: '' });
    }
  }

  // Baugruppen am Ararat-Landeplatz
  if (inArarat) {
    const arUserData = tr.match(/araratGroup\.userData\.([A-Za-z0-9_]+)\s*=\s*(.+);?/);
    const arComment = tr.match(/^\/\/\s*([0-9]+\.\s+[A-ZÄÖÜa-zäöü].+)/);
    if (arUserData) {
      araratAssemblies.push({ line: lineNum, type: 'userData', name: `araratGroup.userData.${arUserData[1]}`, code: arUserData[2].substring(0, 65) });
    } else if (arComment && !tr.includes('===')) {
      araratAssemblies.push({ line: lineNum, type: 'Abschnitt', name: arComment[1].trim(), code: '' });
    }
  }

  // --- E. Top-Level- & Modul-Funktionen ---
  let fnMatch = tr.match(/^(?:window\.)?Arche\.([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)\s*=\s*(?:async\s+)?function\s*\(([^)]*)\)/) ||
                tr.match(/^(?:window\.)?Arche\.([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>/);
  if (fnMatch) {
    const mod = `Arche.${fnMatch[1]}`;
    const name = fnMatch[2];
    const args = fnMatch[3].trim();
    if (functionsByModule[mod]) {
      functionsByModule[mod].push({ line: lineNum, name, args, sig: `${mod}.${name}(${args})` });
    } else {
      functionsByModule['Top-Level & Simulation Core'].push({ line: lineNum, name: `${mod}.${name}`, args, sig: `${mod}.${name}(${args})` });
    }
    continue;
  }

  // Top-Level Function Declaration: function Name(...) (inkl. mehrzeiliger Parameterlisten)
  const topFn = tr.match(/^(?:async\s+)?function\s+([A-Za-z0-9_$]+)\s*\(([^)]*)(?:\)|$)/);
  if (topFn) {
    const name = topFn[1];
    let args = topFn[2].trim();
    if (!tr.includes(')') && i + 1 < totalLines) {
      let k = i + 1;
      while (k < totalLines && k <= i + 8) {
        const nextTr = lines[k].trim();
        const closeIdx = nextTr.indexOf(')');
        if (closeIdx !== -1) {
          args += (args ? ' ' : '') + nextTr.substring(0, closeIdx).trim();
          break;
        } else {
          args += (args ? ' ' : '') + nextTr;
        }
        k++;
      }
    }
    if (args.length > 85) args = args.substring(0, 82) + '...';
    functionsByModule['Top-Level & Simulation Core'].push({ line: lineNum, name, args, sig: `${name}(${args})` });
    continue;
  }

  // --- F. Unit-Tests (T01 bis T101 in runArcheUnitTests) ---
  if (tr.includes('assertTest(') && !tr.includes('function assertTest')) {
    const callIdx = tr.indexOf('assertTest(');
    let sub = tr.substring(callIdx + 11).trim();
    const suiteRes = parseStringLiteral(sub);
    let suite = '';
    let testDesc = '';
    if (suiteRes) {
      suite = suiteRes.value;
      sub = sub.substring(suiteRes.endIndex + 1).trim();
      if (sub.startsWith(',')) sub = sub.substring(1).trim();
      const testRes = parseStringLiteral(sub);
      if (testRes) {
        testDesc = testRes.value;
      }
    }
    const mId = testDesc.match(/^(T\d+)(?::\s*(.*))?$/);
    unitTests.push({
      line: lineNum,
      id: mId ? mId[1] : '?',
      suite,
      name: mId && mId[2] ? mId[2] : testDesc,
      raw: testDesc
    });
  }
}

// 2. Erstelle das strukturierte Markdown-Dokument ARCHE_INDEX.md
let md = `# ARCHE STRUKTUR-INDEX (\`ARCHE_INDEX.md\`)

> **Automatisch generiert durch \`node index_arche.js\`**  
> **Hauptdatei:** [\`${targetFile}\`](file:///${targetPath.replace(/\\/g, '/')})  
> **Umfang:** **${totalLines.toLocaleString('de-DE')} Zeilen** | **${fileSizeKB} KB**  
> **Stand:** ${new Date().toLocaleString('de-DE')}

---

## 📌 GOLDENE ARBEITSREGEL FÜR ALLE KÜNFTIGEN CODE-EDITS:
1. **Lies vor jeder Änderung immer zuerst diesen Index (\`ARCHE_INDEX.md\`)**, um die exakten Zeilennummern der gesuchten Funktionen, Baugruppen oder Tests zu ermitteln.
2. **Springe gezielt** mit \`read_file\` oder \`edit_file\` an die entsprechenden Zeilenbereiche.
3. **Führe nach Abschluss des Edits sofort \`node index_arche.js\` im Terminal aus**, damit die Zeilennummern für den nächsten Arbeitsschritt wieder 100% aktuell sind!

---

## Inhaltsübersicht
- [1. Haupt-Sektionen des Dokuments](#1-haupt-sektionen-des-dokuments)
- [2. Arche Namespaces & Kern-Registries](#2-arche-namespaces--kern-registries)
- [3. Architektur-Meilensteine & Baugruppen-Banner](#3-architektur-meilensteine--baugruppen-banner)
- [4. 3D-Baugruppen (Werftplatz & Ararat-Landeplatz)](#4-3d-baugruppen)
  - [4.1 Werftplatz & Trockendock (\`buildShipyard3D\`)](#41-werftplatz--trockendock-buildshipyard3d)
  - [4.2 Ararat-Landeplatz (\`buildAraratLandingSite3D\`)](#42-ararat-landeplatz-buildararatlandingsite3d)
- [5. Modul- & Top-Level-Funktionen](#5-modul---top-level-funktionen)
  - [5.1 Arche.Procedural (Texturen, POM & Shader)](#51-archeprocedural)
  - [5.2 Arche.Environment (Werft, Ararat & Botanik)](#52-archeenvironment)
  - [5.3 Arche.Fauna (Organische Tiere, Ochsen & Knechte)](#53-archefauna)
  - [5.4 Arche.Physics (Wellen, Ozean, Mikroklima & Schichtpläne)](#54-archephysics)
  - [5.5 Arche.Performance & Quality-Governor](#55-archeperformance)
  - [5.6 Arche.UI & Bilinguale Tooltips](#56-archeui)
  - [5.7 Arche.Player & Kamera-Steuerung](#57-archeplayer)
  - [5.8 Top-Level Engine- & Lifecycle-Funktionen](#58-top-level-engine--lifecycle)
- [6. Vollständiges Unit-Test-Kataster (T01 bis T101)](#6-vollständiges-unit-test-kataster-t01-bis-t101)

---

## 1. Haupt-Sektionen des Dokuments

| Zeile | Tag / Sektion | Beschreibung |
|:-----:|:--------------|:-------------|
`;

docSections.forEach(s => {
  md += `| [\`L${s.line}\`](file:///${targetPath.replace(/\\/g, '/')}#L${s.line}) | \`${s.tag}\` | ${s.desc} |\n`;
});

md += `
---

## 2. Arche Namespaces & Kern-Registries

| Zeile | Namespace | Beschreibung |
|:-----:|:----------|:-------------|
`;

namespaces.forEach(ns => {
  md += `| [\`L${ns.line}\`](file:///${targetPath.replace(/\\/g, '/')}#L${ns.line}) | \`${ns.name}\` | ${ns.desc} |\n`;
});

md += `
---

## 3. Architektur-Meilensteine & Baugruppen-Banner

| Zeile | Abschnitt / Banner-Titel |
|:-----:|:-------------------------|
`;

banners.forEach(b => {
  md += `| [\`L${b.line}\`](file:///${targetPath.replace(/\\/g, '/')}#L${b.line}) | **${b.title}** |\n`;
});

md += `
---

## 4. 3D-Baugruppen

### 4.1 Werftplatz & Trockendock (\`buildShipyard3D\`)
> Bereich: **Zeile ${shipyardStart} bis ${shipyardEnd}** (Funktion \`Arche.Environment.buildShipyard3D\`)

| Zeile | Typ | Baugruppe / Eigenschaft | Details |
|:-----:|:---:|:------------------------|:--------|
`;

shipyardAssemblies.forEach(a => {
  md += `| [\`L${a.line}\`](file:///${targetPath.replace(/\\/g, '/')}#L${a.line}) | \`${a.type}\` | **${a.name}** | \`${a.code}\` |\n`;
});

md += `
### 4.2 Ararat-Landeplatz (\`buildAraratLandingSite3D\`)
> Bereich: **Zeile ${araratStart} bis ${araratEnd}** (Funktion \`Arche.Environment.buildAraratLandingSite3D\`)

| Zeile | Typ | Baugruppe / Eigenschaft | Details |
|:-----:|:---:|:------------------------|:--------|
`;

araratAssemblies.forEach(a => {
  md += `| [\`L${a.line}\`](file:///${targetPath.replace(/\\/g, '/')}#L${a.line}) | \`${a.type}\` | **${a.name}** | \`${a.code}\` |\n`;
});

md += `
---

## 5. Modul- & Top-Level-Funktionen

`;

const moduleKeys = [
  ['Arche.Procedural', '5.1 Arche.Procedural (Texturen, POM & Shader)'],
  ['Arche.Environment', '5.2 Arche.Environment (Werft, Ararat & Botanik)'],
  ['Arche.Fauna', '5.3 Arche.Fauna (Organische Tiere, Ochsen & Knechte)'],
  ['Arche.Physics', '5.4 Arche.Physics (Wellen, Ozean, Mikroklima & Schichtpläne)'],
  ['Arche.Performance', '5.5 Arche.Performance & Quality-Governor'],
  ['Arche.UI', '5.6 Arche.UI & Bilinguale Tooltips'],
  ['Arche.Player', '5.7 Arche.Player & Kamera-Steuerung'],
  ['Top-Level & Simulation Core', '5.8 Top-Level Engine- & Lifecycle-Funktionen']
];

moduleKeys.forEach(([modKey, heading]) => {
  const fns = functionsByModule[modKey] || [];
  md += `### ${heading}\n\n`;
  if (fns.length === 0) {
    md += `*Keine direkten Funktionsdeklarationen in dieser Sektion.*\n\n`;
  } else {
    md += `| Zeile | Funktion / Signatur |\n`;
    md += `|:-----:|:--------------------|\n`;
    fns.forEach(fn => {
      md += `| [\`L${fn.line}\`](file:///${targetPath.replace(/\\/g, '/')}#L${fn.line}) | \`${fn.sig}\` |\n`;
    });
    md += `\n`;
  }
});

md += `
---

## 6. Vollständiges Unit-Test-Kataster (T01 bis T101)

> Ausgeführt durch \`runArcheUnitTests()\` (ab Zeile ~27436).  
> **Gesamt: ${unitTests.length} Tests** — 100% abgedeckt.

| ID | Zeile | Test-Suite | Test-Bezeichnung |
|:--:|:-----:|:-----------|:-----------------|
`;

unitTests.forEach(t => {
  md += `| **${t.id}** | [\`L${t.line}\`](file:///${targetPath.replace(/\\/g, '/')}#L${t.line}) | ${t.suite} | ${t.name} |\n`;
});

md += `
---
*Ende des generierten Index. Bei jeder Code-Modifikation \`node index_arche.js\` im Terminal ausführen!*
`;

// Schreibe ARCHE_INDEX.md
const outPath = path.join(projectDir, 'ARCHE_INDEX.md');
fs.writeFileSync(outPath, md, 'utf8');

console.log(`[index_arche] ARCHE_INDEX.md erfolgreich geschrieben (${(md.length / 1024).toFixed(1)} KB)!`);
console.log(`[index_arche] Erfasst:`);
console.log(`  - ${docSections.length} Dokument-Sektionen`);
console.log(`  - ${namespaces.length} Arche-Namespaces`);
console.log(`  - ${banners.length} Architektur-Banner`);
console.log(`  - ${shipyardAssemblies.length} Werftplatz-Baugruppen`);
console.log(`  - ${araratAssemblies.length} Ararat-Baugruppen`);
let totalFns = 0;
for (const k in functionsByModule) totalFns += functionsByModule[k].length;
console.log(`  - ${totalFns} Funktionen über alle Module`);
console.log(`  - ${unitTests.length} Unit-Tests (T01 bis T101)`);

