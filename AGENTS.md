# AGENTS.md — Projekt-Workflow & Denklevel-Steuerung (`Arche Buch`)

Diese Datei regelt die Rollenverteilung, Modell-/Denklevel-Empfehlungen und verbindlichen Qualitäts-Gates für alle Agenten und Subagenten im Workspace `Arche Buch`.

---

## 1. Projekt-Überblick & zentrale Dateien

- **`Arche Simulation 3.0.html`** — Monolithische Single-File-3D-Simulation (~35.700+ Zeilen, Three.js / WebGL1, EC5-Statik, Hydrostatik, Werftplatz, Ur/Schwemmland, `101` Unit-Tests `T01–T101`).
- **`ARCHE_INDEX.md`** — Automatisch generiertes Inhaltsverzeichnis mit Sektionen, Namespaces, Baugruppen, Funktionszeilen und Test-Ankern.
- **`index_arche.js`** — Index-Generator für `ARCHE_INDEX.md`.
- **`Rohdatei arche.txt`** — Buch- und Fachvorlage (Kapitel/Anforderungen für historische, konstruktive und logistische Details).

---

## 2. Verbindliche Grundregeln (für alle Denklevel)

1. **32k-Zeilen-Schutz:** `Arche Simulation 3.0.html` **niemals** vollständig am Stück lesen. Immer zuerst `ARCHE_INDEX.md` oder gezielte Suche (`Select-String`) nutzen und nur benötigte Blöcke (`StartLine` / `EndLine`, ideal ≤ 150 Zeilen) laden.
2. **Compile- & Index-Pflicht:** Nach jedem Code-Edit zwingend ausführen:
   - `node verify_arche.js` (prüft Datei-Integrität, `vm.Script`-Kompilierung, WebGL1-GLSL, aktualisiert `ARCHE_INDEX.md` über `index_arche.js` und legt bei Änderungen einen Sicherheits-Snapshot in `.backups/` ab)
3. **Qualitäts- & Performance-Gates:**
   - Alle **`101 / 101` Unit-Tests (`T01–T101`)** müssen `PASS` bleiben (keine Statik-/EC5-Formeln verbiegen).
   - **`0` Console-Errors, `0` Page-Errors, `0` WebGL-Shader-Fehler**.
   - **Desktop-Performance (`1440×900`):** Ziel **`~60 FPS`** (Kleinteile über `createStaticGeometryBatcher()` oder `InstancedMesh` bündeln, keine Draw-Call-Explosion).
   - **macOS Safari / WebGL1-Konformität:** Strikt WebGL1-kompatibles GLSL (keine WebGL2-only-Syntax).
   - **100 % Bronzezeit-Authentizität:** Nur Zeder, Eiche, Zypresse, Hainbuche, Basalt, Kalkstein/Travertin, Lehmziegel, Terrakotta, Lapislazuli, Hanfseile, Kopher-Pech, Zinnbronze, Schilf/Leinen, Feuer/Rauch.
4. **Workspace- & Server-Hygiene:**
   - Temporäre Hilfs- oder Prüfskripte ausschließlich in `scratch/` ablegen und nach Abschluss entfernen.
   - PowerShell-Befehle mit `;` verketten (nicht `&&`).
   - Lokale HTTP-Testserver nach Abschluss der Browser-Verifikation sauber beenden.

---

## 3. Denklevel-Matrix nach Rolle & Aufgabe

| Rolle / Aufgabe | Empfohlenes Denklevel | Typische Aufgaben im Projekt | Begründung |
| :--- | :--- | :--- | :--- |
| **Index & Code-Lookup** | **Hydrogen (Low)** *(Subagent: `flash_lite` / `flash`)* | `node index_arche.js` ausführen, Zeilen in `ARCHE_INDEX.md` nachschlagen, `Select-String`-Treffer sammeln, `vm.Script`-Syntaxcheck & Dateigrößen prüfen | Rein mechanisch/deterministisch; minimale Latenz & minimaler Tokenverbrauch |
| **Browser-QA & Screenshot-Check** (`browser`) | **Hydrogen (Low)** *(Standard)* / **Medium** *(bei Fehlerdiagnose)* | Lokale Test-URL (`1440×900`) öffnen, `T01–T101` prüfen, Foreground-FPS (`requestAnimationFrame`) messen, Console/WebGL-Errors auslesen, definierte Kamera-Shots aufnehmen | Feste Prüfcheckliste ohne Code-Eingriff; nur bei tiefergehender Shader-/DOM-Analyse auf Medium eskalieren |
| **3D-Szenenbau & Asset-Politur** | **Hydrogen (Medium)** | Baugruppen in `buildShipyard3D` / `updateLandmarksAndTerrain3D` ergänzen, Bodenkontakt über `evalShipyardTerrainZ(x, y)` sichern, Batcher/`InstancedMesh` erweitern, Ufer-/Kanal-Bauwerke platzieren | Optimale Balance aus räumlichem Verständnis, Edit-Präzision und Geschwindigkeit |
| **GLSL-Shader, Topologie & Performance-Tuning** | **Hydrogen (High)** *(oder **Medium** bei kleinen Parameter-Tweaks)* | Neue/komplexe `onBeforeCompile`-Shader (Wasser, Reflexionen, Kaustiken, `alluvialGroundMat`), Terrain-Durchstiche, komplexe Z-Fighting-/Draw-Call-/FPS-Optimierungen | Verhindert WebGL1-Inkompatibilitäten, Naht-/Clip-Artefakte und subtile Render-Bugs |
| **Statik, Physik & Unit-Tests** | **Hydrogen (High)** | Änderungen an EC5-Statik, Hydrostatik, Lastfällen, Göpel-/Klima-Kopplung (`uWetness`, `uWindVec`, `isThermalMode`), Abgleich mit `Rohdatei arche.txt`, neue/angepasste Tests in `T01–T101` | Null Fehlertoleranz bei physikalischen Formeln und Regressionsschutz |
| **Koordination & Recovery** (Hauptagent) | **Hydrogen (Medium)** *(Regelbetrieb)* / **High** *(große Umbauten / Recovery)* | Aufgaben-Schnitt, Delegation an `research`/`browser`, Abnahme nach Standard-Workflow, Notfall-Wiederherstellung | Hält den Workflow straff und reserviert High-Kontingent für komplexe Architektur- oder Fehlerfälle |

---

## 4. Standard-Abnahme-Workflow

1. **Orientieren (`Low`):** Zielbereich über `ARCHE_INDEX.md` oder `Select-String` lokalisieren und nur den relevanten Zeilenbereich lesen.
2. **Umsetzen (`Medium` / `High`):** Gezielte `edit_file`-Änderungen mit sauberer Geometry-/Material-/Shader-Disziplin.
3. **Indizieren & Kompilieren (`Low`):** `node verify_arche.js` ausführen (`VERIFY_ARCHE_PASS` + `0` Fehler).
4. **Browser-Verifikation (`Low`):** Lokalen HTTP-Server starten, mit Cache-Buster (`?v=...`) im `browser`-Subagent bei `1440×900` prüfen: `101 / 101 PASS`, `0` Errors, `~60 FPS`, Screenshots über `Arche.QA.go('<preset>')` (`shipyard`, `aqueduct`, `ur_city`, `barge_mouth`, `se_mouth`, `east_mouth`, `sw_lake`, `overview`) gezielt aufnehmen.
5. **Sichtprüfung & Abschluss:** Screenshots selbst ansehen, eventuelle Rest-Artefakte beheben, HTTP-Daemon beenden und nur direkt beobachtete Ergebnisse berichten.

