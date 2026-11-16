---
name: arche-3d-builder
description: >-
  Project-specific workflow, coordinate map, Three.js WebGL1 patterns, batching helpers,
  and one-command verification runbook for Arche Simulation 3.0.html. Activate whenever
  inspecting, modifying, debugging, or verifying 3D geometry, shaders, roads, rivers,
  landscapes, or physics/tests in the Arche Buch workspace.
---

# Arche 3D Builder Runbook

Spezialisierter Arbeitsleitfaden für [`Arche Simulation 3.0.html`](../../../Arche%20Simulation%203.0.html) (~36.000 Zeilen Single-File WebGL1/Three.js).

## 1. Vor jedem Edit (32k-Zeilen-Schutz)
1. **Niemals die HTML-Datei komplett einlesen.** Zuerst in [`ARCHE_INDEX.md`](../../../ARCHE_INDEX.md) oder per `Select-String` die exakte Zeilen-Sektion bestimmen, dann nur einen kleinen Block (`≤ 150` Zeilen) per `read_file` laden.
2. **PowerShell-Befehle mit `;` verketten** (niemals `&&`).

## 2. Verbindliche Engine- & Koordinaten-Konventionen
- **Koordinatensystem:** **Z ist OBEN** (`evalShipyardTerrainZ(x, y)` liefert die exakte Gelände-Höhe).
- **Wichtige Ankerkoordinaten (`buildShipyard3D`):**
  - **Helling-Grube (Arche):** `x ∈ [-75, +75]`, `y ∈ [-18, +18]`, Sohle `Z = -0.85 m`, Spundwand `y = ±18.02` (`Z` bis `+1.30`), Flügel-Spundwände `x = -13.15` & `+3.15` (`y = -18..-38`).
  - **Einstiegsrampe & Werkstraße:** Rampenfuß `(-5, -41.5)`, Vorplatz `distRoadX <= 8.0`, Hauptstraße `[2, -45] -> [98, -47.5] -> [131, -48]` (Ur-Westtor) -> `[236, -48]` (Osttor).
  - **Frischwasser-Aquädukt (`X = 58.0`):** Quellgrotte `y = 105..99` -> Quellbecken `(58, 95)` -> 4-Stufen-Kaskade `y = 90.6..78` -> Kopfspeicher `(58, 77.6, Z=16.45)` -> 65-m-Hochgerinne `y = 76.6..11.6` -> Zwillings-Fallrohre `(58, 11.62)` + Crew-Zisterne `(60.2, 13.8)`.
  - **Baudorf Schinar:** `x ≈ 91..122, y ≈ -68..-31`, Brunnenplatz `(101.5, -46.8)`, Tannur-Öfen `(111.8..113.6, -47.2)`, Wachturm `(90, -26)`.
  - **Ur & Wasserwege:** Ur `x ∈ [131, 236], y ∈ [-122, +18]`, Holzhafen `(73, -88.5, r=7.25)`, Euphrat & 5 Kanäle (`BARGE`, `SOUTH`, `SE`, `EAST`, `SW`), 4 Seen (`sw_reeds`, `se_lagoon`, `south_oasis`, `ne_highland`).

## 3. Performance-, Material- & WebGL1-Disziplin
- **Draw-Call-Budget (~60 FPS bei `1440×900`):** Statische Kleinteile **immer** über `createStaticGeometryBatcher()` (`addBox`, `addStrut`, `addCatenaryRope`) oder `THREE.InstancedMesh` bündeln — keine einzelnen Mini-Meshes pro Zaunpfahl/Stein.
- **Z-Fighting verhindern:** Angrenzende horizontale Platten/Straßen im Gelände einbetten (`0.30–0.36 m` Stärke nach unten, `ryTilt = -Math.atan2(zB - zA, segLen)`) und Stöße um `4–8 mm` versetzen oder per `polygonOffset` trennen.
- **Eigene Shader-Materialien (`makeShipyardEnvMat`):**
  - Nur WebGL1-konformes GLSL (`varying`, `texture2D`, `gl_FragColor`, kein `#version 300 es`, kein `out vec4`).
  - Neue Materialien in `shipyardGroup.userData.<matName>` ablegen und in `_setThermalMat`, `_setStructMat` sowie `_restoreMat` registrieren.
  - `waterAquaMat` für Kanäle/Seen, `aqueductFlowMat` für Quell-/Kaskaden-/Gerinne-Wasser, `basaltMasonryMat` für Architektur-Bruchstein (`mechBasalt` für Göpel-Stresstests reserviert).
- **100 % Bronzezeit-Materialtreue:** Nur Zeder, Eiche, Zypresse, Hainbuche, Basalt, Kalkstein/Travertin, Lehmziegel, Terrakotta, Lapislazuli, Hanfseile, Kopher-Pech, Zinnbronze, Schilf/Leinen, Feuer/Rauch.

## 4. Ein-Befehl-Verifikation & Abnahme
1. **Syntax-, WebGL1- & Index-Gate:**
   `node verify_arche.js` -> muss mit `VERIFY_ARCHE_PASS` und `101` indizierten Tests enden (erstellt automatisch Backup in `.backups/`).
2. **Schneller Automatik-QA-Check (Tests, Shader, FPS & Screenshots in einem Lauf):**
   - Vollcheck aller 8 Presets: `node qa_arche.js`
   - Schnellcheck (`shipyard`, `aqueduct`, `overview`): `node qa_arche.js --quick`
   - Erwartung: `QA_ARCHE_PASS`, **`101 / 101 PASS`**, **`0` Console-/Page-/Shader-Errors**, **`~60 FPS`** bei `1440×900`.
3. **Sichtprüfung:** Erzeugte PNGs in [`scratch/`](../../../scratch/) mit `read_file` visuell prüfen und temporäre Dateien in `scratch/` nach Abschluss aufräumen.

