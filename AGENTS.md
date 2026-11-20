# AGENTS.md — Projekt-Workflow & Qualitäts-Gates (`Arche Buch`)

Diese Datei regelt den schlanken **Single-Agent-Workflow** (ohne unnötigen Subagenten-Overhead), die Aufgaben-Steuerung und die verbindlichen Qualitäts-Gates für alle KI-Sessions im Workspace `Arche Buch`.

---

## 1. Projekt-Überblick & zentrale Dateien

- **`Arche Simulation 3.0.html`** — Monolithische Single-File-3D-Simulation (~47.700+ Zeilen, Three.js r128 / WebGL1, EC5-Statik, Hydrostatik, Werftplatz, Ur-Schinar, Ararat, `101` Unit-Tests `T01–T101`).
- **`ARCHE_INDEX.md`** — Automatisch generiertes Inhaltsverzeichnis mit Sektionen, Namespaces, Baugruppen, Funktionszeilen und Test-Ankern.
- **`index_arche.js`** — Index-Generator für `ARCHE_INDEX.md`.
- **`verify_arche.js`** — Ein-Befehl-Gate: Datei-Integrität, `vm.Script`-Kompilierung, WebGL1-GLSL-Check, Index-Update & atomares `.backups/`-Snapshot.
- **`qa_arche.js`** — Ein-Befehl-Browser-QA-Runner (CDP, `1440×900` & `1920×1080`, `--quick`, `--critic`, `--ipad`, `--no-shots`, Draw-Call-Budget & Screenshots nach `scratch/`).
- **`rules/visual-critic.md`** — Verbindliches 7-Punkte-Visual-Critic-Gate für `scratch/qa_*.png` und `assets/previews/*.png`.
- **`BLENDER_PIPELINE.md`** — Verbindlicher Asset-, Koordinaten-, Material-, 4-LOD- & `.glb`-Pipeline-Standard für alle Blender-Geometrien.
- **`Rohdatei arche.txt`** — Buch- und Fachvorlage (Kapitel/Anforderungen für historische, konstruktive und logistische Details).

---

## 2. Verbindliche Grundregeln (für alle Sessions & Modelle)

1. **Single-Agent- & Quota-Schutz (KEINE unnötigen Subagenten!):**
   - Spawne **keine** `research`-, `browser`- oder `flash`-Subagenten.
   - Orientierung erfolgt direkt über `ARCHE_INDEX.md` oder gezieltes `Select-String`; Browser-Prüfung, FPS-Messung und Screenshots erfolgen ausschließlich deterministisch über **`node qa_arche.js`**.
2. **40k-Zeilen-Schutz:** `Arche Simulation 3.0.html` **niemals** vollständig am Stück lesen. Immer zuerst `ARCHE_INDEX.md` oder `Select-String` nutzen und nur gezielte Blöcke (ideal `≤ 150` Zeilen) laden.
3. **Compile- & Index-Pflicht:** Nach jedem Code-Edit zwingend **`node verify_arche.js`** ausführen (`VERIFY_ARCHE_PASS` + aktueller `ARCHE_INDEX.md` + Snapshot in `.backups/`).
4. **Physik-, Authentizitäts- & Test-Gates:**
   - Alle **`101 / 101` Unit-Tests (`T01–T101`)** müssen `PASS` bleiben (**striktes Verbot**, EC5-/Statik-/Physikbeiwerte künstlich zu verbiegen).
   - **`0` Console-Errors, `0` Page-Errors, `0` WebGL-Shader-Fehler**.
   - **macOS Safari / WebGL1-Konformität:** Strikt WebGL1-kompatibles GLSL (keine WebGL2-only-Syntax).
   - **100 % Bronzezeit-Authentizität:** Nur Zeder, Eiche, Zypresse, Hainbuche, Basalt, Kalkstein/Travertin, Lehmziegel, Terrakotta, Lapislazuli, Hanfseile, Kopher-Pech, Zinnbronze, Schilf/Leinen, Feuer/Rauch.
   - **Rumpf-/Arche-Farben & Rendering-Reinheit:** Kopher-Pech und Außenholz der Arche bleiben unangetastet, sofern nicht ausdrücklich anders beauftragt. Natives Blender-4-AgX (`THREE.CustomToneMapping`), `SSCS` und Detail-Normals sind **nur im `TEXTURED`-Modus** aktiv; `EC5`- und `THERMAL`-Ansichten nutzen strikt `NoToneMapping` und bleiben 100 % unverfälscht.
5. **Draw-Call-, Schatten- & Performance-Schutz (Pflicht für jedes Feature!):**
   - **Desktop-Ziel (`1440×900` & `1920×1080`):** **`~55–60 FPS`** bei einem Desktop-Budget von **`2,0–3,0 Mio. Tris`** und **`<= 350` Draw-Calls** (strenge Einhaltung der Draw-Call-Obergrenzen in `qa_arche.js`).
   - **Kein `new THREE.Mesh(...)` in Schleifen:** Starre Baugruppen zwingend über `createStaticGeometryBatcher()` bzw. räumliche Chunks bündeln; wiederholte Objekte (`≥ 4` Stück) zwingend als `THREE.InstancedMesh` (`frustumCulled = false` bei bewegten Instanzen, `visible = false` wenn `count === 0`).
   - **Material-Sortierung vor `geo.addGroup`:** Dreiecke nach Material-ID sortieren (`1` Group pro Material statt fragmentierter Draw-Calls).
   - **Schatten als Opt-In (`castShadow = false` als Standard):** Nur große Hauptbauwerke und nahe Bäume (`LOD0/1`) dürfen Schatten werfen; Gräser, Feldpflanzen, Kleindeko und Fernobjekte bleiben `castShadow = false`.
   - **Master-Shader- & Shader-Budget-Pflicht (Dauerhafter Shader-Wächter):** Neue Assets/Kits nutzen zwingend die bestehenden Master-Shader (`arche_blender_botany_v5_*`, `arche_world_trim_unified_v1`, `arche_env_prop_uber_v1`, `arche_fauna_v7_UNIFIED`, `arche_sy_aqua_unified_v1`, `attachArcheMaterialHooks`) über **Uniforms** und konsistente Flag-Signaturen (`Arche.Procedural.DUMMY_TEX` 1×1-Dummy-Texturen für optionale Slots wie `emissiveMap`/`aoMap`/`normalMap`/`roughnessMap`) statt neuer `onBeforeCompile`-Programme oder neuer `customProgramCacheKey`s. Der Shader-Wächter in `qa_arche.js` erzwingt `totalPrograms <= maxPrograms` (`50` Desktop / `55` iPad) sowie `deltaPrograms === 0` zwischen Ladescreen-Ende und allen Werft-Presets.
   - **Maus-Raycast-Disziplin:** `perform3DRaycastInspect` bleibt gethrottelt (`≥ 90 ms`), pausiert beim Orbit-Drag und ignoriert reine Terrain-/Deko-Meshes ohne Tooltip.
6. **Workspace- & Server-Hygiene:**
   - Temporäre Hilfs- oder Prüfskripte ausschließlich in `scratch/` ablegen und nach Abschluss bereinigen.
   - PowerShell-Befehle mit `;` verketten (nicht `&&`).
   - Gestartete HTTP-Testserver nach Abschluss sauber beenden (`node qa_arche.js` startet und schließt seinen Server selbstständig).

---

## 3. Aufgaben-Matrix & empfohlene Modell-/Denkstufe

*(Ohne Subagenten — immer als 1 direkter Hauptagent pro frischem Chat arbeiten!)*

| Aufgaben-Typ | Empfohlenes Modell / Denklevel | Typische Aufgaben im Projekt |
| :--- | :--- | :--- |
| **Kleine Fixes, Verify & Doku** | **Gemini 4 Neon (Low)** | `node verify_arche.js`, Zeilen-Lookup, Doku-Sync, Text-/Tooltip-/UI-Kleinänderungen |
| **Standard-Arbeit (~90 % aller Tasks)** | **Gemini 4 Neon (Medium)** *(Fallback: **Claude Sonnet 5.5 Medium**)* | 3D-Szenenbau (`buildShipyard3D` / `buildAraratLandingSite3D`), Blender-`bpy`-Assets, UI, Kamera-Tours, Shader-/LOD-Pflege, `qa_arche.js`-Lauf & Screenshot-Abnahme |
| **Harte Groß-Integrationen, EC5 & Arche-Umbau** | **Gemini 4 Neon (High)** *(Fallback: **Claude Sonnet 5.5 Medium**)* | Komplexe Groß-Integrationen, Arche-Strukturumbauten, EC5-Statik, D'Alembert, Hydrostatik, Klima-/Veterinär-Kern, `T01–T101` |

---

## 4. Standard-Abnahme-Workflow (4 saubere Schritte)

1. **Orientieren:** Zielbereich direkt über `ARCHE_INDEX.md` oder `Select-String` lokalisieren und nur den relevanten Zeilenbereich lesen.
2. **Umsetzen:** Gezielte `edit_file`-Änderungen mit strikter Einhaltung von Abschnitt 2 (Draw-Calls, Batching, WebGL1, keine Arche-Farbänderung).
3. **Verifizieren (Node.js):** `node verify_arche.js` ausführen → **`VERIFY_ARCHE_PASS`** (`0` Fehler, `ARCHE_INDEX.md` aktuell).
4. **Browser-QA & Visual Critic:** `node qa_arche.js` (bei großen Änderungen inkl. `--ipad`, bei schnellen Checks `--quick`) ausführen → **`QA_ARCHE_PASS`** (`101 / 101 PASS`, `0` Console-/Page-/Shader-Errors, Draw-Call-Budget eingehalten, `~60 FPS`). Anschließend alle betroffenen `scratch/qa_*.png` sowie `assets/previews/*.png` streng nach **`rules/visual-critic.md`** prüfen (alle 7 Kriterien mit `PASS` / `MINOR` / `FAIL`) und bei `FAIL` nachbessern.