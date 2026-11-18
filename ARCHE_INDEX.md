# ARCHE STRUKTUR-INDEX (`ARCHE_INDEX.md`)

> **Automatisch generiert durch `node index_arche.js`**  
> **Hauptdatei:** [`Arche Simulation 3.0.html`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html)  
> **Umfang:** **47.714 Zeilen** | **2831.2 KB**  
> **Stand:** 18.11.2026, 12:39:29

---

## 📌 GOLDENE ARBEITSREGEL FÜR ALLE KÜNFTIGEN CODE-EDITS:
1. **Lies vor jeder Änderung immer zuerst diesen Index (`ARCHE_INDEX.md`)**, um die exakten Zeilennummern der gesuchten Funktionen, Baugruppen oder Tests zu ermitteln.
2. **Springe gezielt** mit `read_file` oder `edit_file` an die entsprechenden Zeilenbereiche.
3. **Führe nach Abschluss des Edits sofort `node index_arche.js` im Terminal aus**, damit die Zeilennummern für den nächsten Arbeitsschritt wieder 100% aktuell sind!

---

## Inhaltsübersicht
- [1. Haupt-Sektionen des Dokuments](#1-haupt-sektionen-des-dokuments)
- [2. Arche Namespaces & Kern-Registries](#2-arche-namespaces--kern-registries)
- [3. Architektur-Meilensteine & Baugruppen-Banner](#3-architektur-meilensteine--baugruppen-banner)
- [4. 3D-Baugruppen (Werftplatz & Ararat-Landeplatz)](#4-3d-baugruppen)
  - [4.1 Werftplatz & Trockendock (`buildShipyard3D`)](#41-werftplatz--trockendock-buildshipyard3d)
  - [4.2 Ararat-Landeplatz (`buildAraratLandingSite3D`)](#42-ararat-landeplatz-buildararatlandingsite3d)
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
| [`L15`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15) | `<script>` | Beginn Haupt-JavaScript (Three.js & Arche Engine) |
| [`L16`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16) | `<script>` | Beginn Haupt-JavaScript (Three.js & Arche Engine) |
| [`L17`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17) | `<script>` | Beginn Haupt-JavaScript (Three.js & Arche Engine) |
| [`L18`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18) | `<script>` | Beginn Haupt-JavaScript (Three.js & Arche Engine) |
| [`L19`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19) | `<script>` | Beginn Haupt-JavaScript (Three.js & Arche Engine) |
| [`L20`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20) | `<style>` | CSS-Stylesheets & UI-Design |
| [`L1477`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L1477) | `</style>` | Ende CSS-Stylesheets |
| [`L1480`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L1480) | `<body...>` | DOM-Hierarchie, HUD-Container & Canvas |
| [`L2012`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2012) | `<script>` | Beginn Haupt-JavaScript (Three.js & Arche Engine) |
| [`L47711`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47711) | `</script>` | Ende Haupt-JavaScript |
| [`L47712`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47712) | `</body>` | Ende DOM-Hierarchie |

---

## 2. Arche Namespaces & Kern-Registries

| Zeile | Namespace | Beschreibung |
|:-----:|:----------|:-------------|
| [`L2015`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2015) | `window.Arche` | Arche Root-Namespace & State/Config/Kinematik-Arrays |
| [`L2187`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2187) | `Arche.UI` | UI-DOM-Bindings, Bilinguale Tooltips (DE/EN) & Viewport-Sync |
| [`L3089`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L3089) | `Arche.I18n` | Bilinguale Sprach-Engine (DE/EN), GUI-Labels & Option-Maps |
| [`L6695`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6695) | `Arche.Groups` | Three.js Szenengruppen-Registry (hullGroup, interiorGroup, shipyardGroup, etc.) |
| [`L8046`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8046) | `Arche.Materials` | Material-Registry (Gopherholz, Eiche, Zypresse, Bronze, Wasser, etc.) |
| [`L35059`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35059) | `Arche.Performance` | Auto-FPS-Governor (Tier 1-4 Quality-Manager) & Instanz-Reduktion |

---

## 3. Architektur-Meilensteine & Baugruppen-Banner

| Zeile | Abschnitt / Banner-Titel |
|:-----:|:-------------------------|
| [`L8083`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8083) | **BLENDER -> ARCHE .GLB-ASSET-PIPELINE (Arche.Assets)** |
| [`L17258`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17258) | **ANALYTISCHER 3D-KOLLISIONS-, FASS- & GANG-FREIHALTE-SOLVER (PBD, 14 ITER.)** |
| [`L18953`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18953) | **2. Z-Up-Geometrie-Helfer (Z ist OBEN!) & Ausrichtungs-Funktionen** |
| [`L18984`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18984) | **3. Höhenfunktionen & Geometrie-Helfer für Steppe und Hochgebirge** |
| [`L19876`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19876) | **PROZEDURALE BOTANIK: 4-QUADRANTEN-ATLAS & 3-STUFIGE VERÄSTELUNG (PAKET 1E)** |
| [`L21522`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21522) | **3B. Ultraleichter 12-km-Fernhorizont-Ring (~1.792 Tris, 0 % Weltkante)** |
| [`L21640`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21640) | **3C. 4-Band-Schatten-LOD-Helfer (Höhentextur-Bake + Projizierte GPU-Schatten)** |
| [`L22045`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22045) | **4. Kompletter Neuaufbau des Werftplatzes (Arche.Environment.buildShipyard3D)** |
| [`L23826`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23826) | **BAUGRUPPE 1: Baumfäll-Szene im Primärwald & Rollenträger-Knechte (Kap. 13.1)** |
| [`L24086`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24086) | **BAUGRUPPE 2: Göpel-Sägewerk, drehender Rotor, Kurbelschleife & Sägegruben (Kap. 13.1)** |
| [`L24390`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24390) | **BAUGRUPPE 3: 4 Holzkohlemeiler, Tubal-Kain-Schmiede & 9 Rauchsäulen (Kap. 13.1 & 13.2)** |
| [`L29776`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29776) | **4B. ASYNCHRONE BLENDER-BOTANIK-HYDRATION (6 ARTEN x 15 VARIANTEN x LOD0/LOD1)** |
| [`L33108`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33108) | **3. Exakte Höhen-Synchronisation & Ausblenden des schwarzen seaGrid** |
| [`L36596`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36596) | **SYSTEM 1 (aPathType = 0.0): Vordere Frischluft-Schachtkammer & Erdregister |ZUL.|** |
| [`L36683`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36683) | **SYSTEM 2 (aPathType = 1.0 & 1.5): Stall-Durchstroemung & echte Tuer-Durchtritte** |
| [`L36725`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36725) | **SYSTEM 3 (aPathType = 2.0): Thermik, 1-Elle-Silospalt, Badgir-Lee-Kammer & Zohar** |
| [`L36898`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36898) | **SYSTEM 4 (aPathType = 3.0): Offenes 9x8-Ellen-Seitentor S7** |
| [`L44136`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44136) | **Screen-Space Contact Shadows (SSCS, Half-Res Depth, Desktop Tier 0/1, WebGL1)** |
| [`L46213`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46213) | **SUITE 1: 1. Ellen-Kanon, EN 338 & Clean Architecture (T01–T07)** |
| [`L46262`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46262) | **SUITE 2: 2. Hydrostatik, Massenbilanz & Schwimmstabilität (T08–T18)** |
| [`L46348`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46348) | **SUITE 3: 3. Wellenkinematik & 6-DOF-Hydrodynamik (T19–T30)** |
| [`L46427`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46427) | **SUITE 4: 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik (T31–T53)** |
| [`L46660`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46660) | **SUITE 5: 5. 371-Tage-Chronik, Ermüdung & Instandhaltung (T54–T56)** |
| [`L46702`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46702) | **SUITE 6: 6. Holz-Stein-Maschinenbau, Silos & Einbauten (T57–T71)** |
| [`L46804`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46804) | **SUITE 7: 7. Meteorologie, Bauphysik & Veterinär-Physiologie (T72–T92)** |
| [`L46980`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46980) | **SUITE 8: 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität (T93–T101)** |

---

## 4. 3D-Baugruppen

### 4.1 Werftplatz & Trockendock (`buildShipyard3D`)
> Bereich: **Zeile 22047 bis 31175** (Funktion `Arche.Environment.buildShipyard3D`)

| Zeile | Typ | Baugruppe / Eigenschaft | Details |
|:-----:|:---:|:------------------------|:--------|
| [`L22051`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22051) | `userData` | **shipyardGroup.userData.cribbingBlocks** | `[];` |
| [`L22052`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22052) | `userData` | **shipyardGroup.userData.pitchPits** | `[];` |
| [`L22064`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22064) | `userData` | **shipyardGroup.userData.heightMapTex** | `bakedSy.tex;` |
| [`L22067`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22067) | `Abschnitt` | **1. Topografisches Trockendock-Becken & Quellgebirge (1600 x 1600 m, 240 x 240 Segmente)** | `` |
| [`L22093`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22093) | `userData` | **shipyardGroup.userData.basinMesh** | `terrainMesh;` |
| [`L22125`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22125) | `userData` | **shipyardGroup.userData.horizonRingMesh** | `syHorizon.mesh;` |
| [`L22126`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22126) | `userData` | **shipyardGroup.userData.horizonMat** | `syHorizon.mat;` |
| [`L22174`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22174) | `userData` | **shipyardGroup.userData.waterAquaMat** | `waterAquaMat;` |
| [`L22201`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22201) | `userData` | **shipyardGroup.userData.basaltMasonryMat** | `basaltMat;` |
| [`L22237`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22237) | `userData` | **shipyardGroup.userData.aqueductFlowMat** | `aqueductFlowMat;` |
| [`L22256`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22256) | `userData` | **shipyardGroup.userData.canalBedMat** | `canalBedMat;` |
| [`L22290`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22290) | `userData` | **shipyardGroup.userData.canalWaterBedMat** | `canalWaterBedMat;` |
| [`L22383`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22383) | `userData` | **shipyardGroup.userData.riverWaterMat** | `riverWaterMat;` |
| [`L22406`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22406) | `userData` | **shipyardGroup.userData.flagstoneMat** | `flagstoneMat;` |
| [`L22424`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22424) | `userData` | **shipyardGroup.userData.lapisFriezeMat** | `lapisFriezeMat;` |
| [`L22437`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22437) | `userData` | **shipyardGroup.userData.ochreAwningMat** | `ochreAwningMat;` |
| [`L22508`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22508) | `Abschnitt` | **3. Die 60-Ellen-Beladerampe zum Seitentor (Backbord @ X = -5.0 m)** | `` |
| [`L22531`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22531) | `userData` | **shipyardGroup.userData.mainRampMesh** | `deckMesh;` |
| [`L22591`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22591) | `Abschnitt` | **3. Animierte Beladungs-Karawane vor der Flut (boardingGroup)** | `` |
| [`L22595`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22595) | `userData` | **shipyardGroup.userData.boardingGroup** | `boardingGroup;` |
| [`L22597`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22597) | `userData` | **shipyardGroup.userData.boardingWalkers** | `boardingWalkers;` |
| [`L22670`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22670) | `userData` | **shipyardGroup.userData.caravanMeta** | `caravanMeta;` |
| [`L22739`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22739) | `userData` | **shipyardGroup.userData.caravanInstMesh** | `caravanInstMesh;` |
| [`L22778`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22778) | `userData` | **shipyardGroup.userData.shipyardBirdsInstMesh** | `shipyardBirdsInstMesh;` |
| [`L22781`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22781) | `userData` | **shipyardGroup.userData.impactFX** | `Arche.Fauna.createGroundImpactFX(shipyardGroup, 64, 56, false);` |
| [`L22789`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22789) | `userData` | **shipyardGroup.userData.bunkeringGroup** | `bunkeringGroup;` |
| [`L22791`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22791) | `userData` | **shipyardGroup.userData.bunkeringWalkers** | `bunkeringWalkers;` |
| [`L22803`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22803) | `userData` | **shipyardGroup.userData.sackMat** | `sackMat;` |
| [`L22927`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22927) | `Abschnitt` | **4. Zugbrücken-Klappe (drawbridgeFlapGroup)** | `` |
| [`L22953`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22953) | `userData` | **shipyardGroup.userData.bronzeToolMat** | `bronzeToolMat;` |
| [`L22960`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22960) | `userData` | **shipyardGroup.userData.smithyMetalMat** | `smithyMetalMat;` |
| [`L22999`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22999) | `userData` | **shipyardGroup.userData.mudbrickMat** | `mudbrickMat;` |
| [`L23014`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23014) | `userData` | **shipyardGroup.userData.reedThatchMat** | `reedThatchMat;` |
| [`L23024`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23024) | `userData` | **shipyardGroup.userData.dryWorkers** | `[];` |
| [`L23067`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23067) | `userData` | **shipyardGroup.userData.scaffolds** | `[];` |
| [`L23375`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23375) | `userData` | **shipyardGroup.userData.craneWinchInstMeshes** | `_winchInstMeshes;` |
| [`L23376`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23376) | `userData` | **shipyardGroup.userData.craneOxInst** | `_craneOxInst;` |
| [`L23377`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23377) | `userData` | **shipyardGroup.userData.craneOxLocals** | `_craneOxLocals;` |
| [`L23388`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23388) | `userData` | **shipyardGroup.userData.craneHoistGroups** | `craneHoistGroups;` |
| [`L23389`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23389) | `userData` | **shipyardGroup.userData.craneWinchRotors** | `craneWinchRotors;` |
| [`L23391`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23391) | `Abschnitt` | **7. Kopher-Pechsiederei (3 Rundöfen mit glühendem Bad, Pechsiedern & Kalfater-Werkzeuglager)** | `` |
| [`L23580`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23580) | `userData` | **shipyardGroup.userData.smithyEmberMat** | `smithyEmberMat;` |
| [`L23592`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23592) | `userData` | **shipyardGroup.userData.terracottaMat** | `terracottaMat;` |
| [`L23708`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23708) | `userData` | **shipyardGroup.userData.hayMat** | `hayMat;` |
| [`L23743`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23743) | `Abschnitt` | **10. Kapitel 13: Holzriese & Rollenbahn (mit stackBatch zusammengefasst)** | `` |
| [`L23826`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23826) | `Kapitel 13 Baugruppe` | **BAUGRUPPE 1: Baumfäll-Szene im Primärwald & Rollenträger-Knechte (Kap. 13.1)** | `` |
| [`L23835`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23835) | `Abschnitt` | **1. Stehender 22-m-Zedernriese (D = 1.56 m) mit 3D-POM-Zedernborke, 4 Wurzelanläufen, einseitigem Kernholz-Fallkerb & 3-stufiger Krone** | `` |
| [`L23930`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23930) | `Abschnitt` | **3. Seilzug in der Krone + Umlenkrolle + 4 Zugochsen als 2 Doppelgespanne (Kettenlinie mit Durchhang)** | `` |
| [`L23980`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23980) | `Abschnitt` | **4. Nachbar-Baumstumpf (-139.2, -96.8) & waagerecht am Boden liegender 20-m-Zedernstamm ([-138.0, -96.0] bis [-122.0, -84.0]) mit 3D-POM-Zedernborke** | `` |
| [`L24082`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24082) | `userData` | **shipyardGroup.userData.fellingSceneGroup** | `fellingSceneGroup;` |
| [`L24086`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24086) | `Kapitel 13 Baugruppe` | **BAUGRUPPE 2: Göpel-Sägewerk, drehender Rotor, Kurbelschleife & Sägegruben (Kap. 13.1)** | `` |
| [`L24095`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24095) | `Abschnitt` | **1. Basalt-Bruchsteinring (R = 4.0 m) auf dem ebenen +2.80 m Plateau** | `` |
| [`L24103`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24103) | `Abschnitt` | **2. Feststehendes Eichen-Galgenportal & Basalt-Spurlager über dem Göpel** | `` |
| [`L24113`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24113) | `Abschnitt` | **3. Drehbare Untergruppe: sawmillCapstanRotor (Königswelle, Kammrad & Joche gebatcht + 4 gehörnte Zugochsen)** | `` |
| [`L24165`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24165) | `userData` | **shipyardGroup.userData.sawmillCapstanRotor** | `sawmillCapstanRotor;` |
| [`L24167`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24167) | `Abschnitt` | **4. Drehende Vorgelegewelle mit 8er-Stockritzel, Schwungrad & Kurbelzapfen (sawDriveShaftRotor)** | `` |
| [`L24174`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24174) | `userData` | **shipyardGroup.userData.sawdustMat** | `sawdustMat;` |
| [`L24214`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24214) | `userData` | **shipyardGroup.userData.sawDriveShaftRotor** | `sawDriveShaftRotor;` |
| [`L24216`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24216) | `Abschnitt` | **5. Lagerung der Vorgelegewelle: Oberer Längsträger über der Ochsenbahn (0 % Spur-Kollision!) + Außen-Lagerbock bei x = sx0 + 4.65** | `` |
| [`L24252`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24252) | `Abschnitt` | **6. Vertikales Sägegatter mit separat gelenkter Pleuelstange (Kurbelschleife)** | `` |
| [`L24268`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24268) | `userData` | **shipyardGroup.userData.sawFrame** | `sawFrameMesh;` |
| [`L24269`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24269) | `userData` | **shipyardGroup.userData.sawFrameBaseZ** | `sz0 + 1.2;` |
| [`L24281`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24281) | `userData` | **shipyardGroup.userData.sawPitmanGroup** | `sawPitmanGroup;` |
| [`L24282`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24282) | `userData` | **shipyardGroup.userData.sawPitmanBaseZ** | `sz0 + 1.82;` |
| [`L24283`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24283) | `userData` | **shipyardGroup.userData.sawPitmanCenterY** | `sy0;` |
| [`L24284`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24284) | `userData` | **shipyardGroup.userData.sawCrankCenterZ** | `sz0 + 2.62;` |
| [`L24386`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24386) | `userData` | **shipyardGroup.userData.sawPitGroup** | `sawPitGroup;` |
| [`L24390`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24390) | `Kapitel 13 Baugruppe` | **BAUGRUPPE 3: 4 Holzkohlemeiler, Tubal-Kain-Schmiede & 9 Rauchsäulen (Kap. 13.1 & 13.2)** | `` |
| [`L24406`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24406) | `userData` | **shipyardGroup.userData.meilerDomeMat** | `meilerDomeMat;` |
| [`L24416`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24416) | `userData` | **shipyardGroup.userData.meilerHotMat** | `meilerHotMat;` |
| [`L24467`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24467) | `userData` | **shipyardGroup.userData.smokeMat** | `smokeMat;` |
| [`L24494`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24494) | `userData` | **shipyardGroup.userData.smokePlumesGroup** | `smokePlumesGroup;` |
| [`L24495`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24495) | `userData` | **shipyardGroup.userData.smokePuffs** | `smokePuffs;` |
| [`L24511`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24511) | `userData` | **shipyardGroup.userData.smithyAnvilMat** | `smithyAnvilMat;` |
| [`L24610`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24610) | `userData` | **shipyardGroup.userData.smithyToolsGroup** | `smithyToolsGroup;` |
| [`L24613`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24613) | `Abschnitt` | **13. Kapitel 13: Frischwasser-Aquädukt & Raubtier-Rollkäfige** | `` |
| [`L25725`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25725) | `userData` | **shipyardGroup.userData.blenderOrnamentalSpecs** | `blenderOrnamentalSpots;` |
| [`L26001`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26001) | `Abschnitt` | **1. Nord-Vorstadt (außerhalb Nord-Königstor bei y=+36..+52)** | `` |
| [`L26004`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26004) | `Abschnitt` | **2. Süd-Vorstadt (außerhalb Süd-Karawanentor bei y=-136..-162)** | `` |
| [`L26007`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26007) | `Abschnitt` | **3. Ostufer-Brückenkopf & Karawanserei (x=272..294, y=-68..-28)** | `` |
| [`L26464`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26464) | `userData` | **shipyardGroup.userData.cityBoats** | `cityBoats;` |
| [`L26515`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26515) | `userData` | **shipyardGroup.userData.cityWalkers** | `cityWalkers;` |
| [`L26760`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26760) | `Abschnitt` | **1. Ur-Schinar Süd & Südwest-Schwemmland (10 große Parzellen)** | `` |
| [`L26771`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26771) | `Abschnitt` | **2. Ur-Ostufer / Euphrat-Ostebene gegenüber der Metropole (10 weite Parzellen)** | `` |
| [`L26782`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26782) | `Abschnitt` | **3. Nisaba-Kornkammer / Südwest-Ebene (10 weite Parzellen)** | `` |
| [`L26793`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26793) | `Abschnitt` | **4. Eridu-Lagunengürtel / Südost-Ebene (8 große Parzellen)** | `` |
| [`L26802`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26802) | `Abschnitt` | **5. Girsu-Kanalauen / Ost-Ebene (8 weite Parzellen)** | `` |
| [`L26811`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26811) | `Abschnitt` | **6. Sippar & Nord-Euphrattal (6 große Parzellen)** | `` |
| [`L26818`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26818) | `Abschnitt` | **7. Larsam-Südoase / Süd-Weide & Getreidegürtel (6 weite Parzellen)** | `` |
| [`L27092`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27092) | `userData` | **shipyardGroup.userData.procCropInstMesh** | `cropInstMesh;` |
| [`L27093`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27093) | `userData` | **shipyardGroup.userData.blenderCropSpecs** | `{` |
| [`L27207`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27207) | `Abschnitt` | **1. Ur-Schinar Süd & SW (12)** | `` |
| [`L27214`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27214) | `Abschnitt` | **2. Ur-Ostufer gegenüber Metropole (12)** | `` |
| [`L27221`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27221) | `Abschnitt` | **3. Nisaba Kornkammer (12)** | `` |
| [`L27228`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27228) | `Abschnitt` | **4. Eridu Lagunengürtel (8)** | `` |
| [`L27233`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27233) | `Abschnitt` | **5. Girsu Ost-Ebene (8)** | `` |
| [`L27238`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27238) | `Abschnitt` | **6. Sippar & Nord-Euphrattal (6)** | `` |
| [`L27242`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27242) | `Abschnitt` | **7. Larsam Südoase (6)** | `` |
| [`L27359`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27359) | `userData` | **shipyardGroup.userData.farmInsts** | `{` |
| [`L27371`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27371) | `userData` | **shipyardGroup.userData.farmMovers** | `farmMovers;` |
| [`L27429`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27429) | `userData` | **shipyardGroup.userData.shadufInsts** | `shadufInsts;` |
| [`L27430`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27430) | `userData` | **shipyardGroup.userData.shadufBeams** | `shadufBeams;` |
| [`L27465`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27465) | `userData` | **shipyardGroup.userData.waterWheels** | `waterWheels;` |
| [`L27481`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27481) | `userData` | **shipyardGroup.userData.waterFoamMat** | `waterFoamMat;` |
| [`L27531`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27531) | `userData` | **shipyardGroup.userData.waterFoamInstMesh** | `waterFoamInstMesh;` |
| [`L27532`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27532) | `userData` | **shipyardGroup.userData.waterFoamNodes** | `foamNodes;` |
| [`L27533`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27533) | `userData` | **shipyardGroup.userData.waterFoamWakeStart** | `wakeSlotStart;` |
| [`L27546`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27546) | `userData` | **shipyardGroup.userData.cityBuildingShadowsInstMesh** | `bldgShadowInst;` |
| [`L27637`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27637) | `userData` | **shipyardGroup.userData.magurInstMeshes** | `boatParts.map(p => p.inst);` |
| [`L27638`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27638) | `userData` | **shipyardGroup.userData.updateMagurBoatMatrix** | `(bt, mat4) => {` |
| [`L27747`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27747) | `userData` | **shipyardGroup.userData.cityWalkerInstMeshes** | `cityWalkerInstMeshes;` |
| [`L27766`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27766) | `userData` | **shipyardGroup.userData.smokeInstMesh** | `smokeInst;` |
| [`L27865`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27865) | `userData` | **shipyardGroup.userData.boulderMat** | `boulderMat;` |
| [`L27921`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27921) | `userData` | **shipyardGroup.userData.boulderInstMesh** | `boulderInstMesh;` |
| [`L27942`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27942) | `userData` | **shipyardGroup.userData.logYardMat** | `logYardMat;` |
| [`L27982`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27982) | `userData` | **shipyardGroup.userData.logYardInstMesh** | `logYardInstMesh;` |
| [`L28162`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28162) | `userData` | **shipyardGroup.userData.steppeGrassInstMesh** | `steppeGrassInstMesh;` |
| [`L28163`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28163) | `userData` | **shipyardGroup.userData.blenderGrassSpecs** | `{ count: gPlaced, transforms: gPlaceTf, kind: gPlaceKind, colors:` |
| [`L28347`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28347) | `userData` | **shipyardGroup.userData.steppeShrubInstMesh** | `shrubInstMeshes[0];` |
| [`L28348`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28348) | `userData` | **shipyardGroup.userData.shrubInstMeshes** | `shrubInstMeshes;` |
| [`L28349`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28349) | `userData` | **shipyardGroup.userData.procShrubMeshes** | `shrubInstMeshes.slice();` |
| [`L28384`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28384) | `userData` | **shipyardGroup.userData.stumpBarkMat** | `stumpBarkMat;` |
| [`L28385`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28385) | `userData` | **shipyardGroup.userData.stumpCutMat** | `stumpCutMat;` |
| [`L28434`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28434) | `userData` | **shipyardGroup.userData.treeStumps** | `stumpsGroup;` |
| [`L28941`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28941) | `userData` | **shipyardGroup.userData.treesGroup** | `treesGroup;` |
| [`L28942`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28942) | `userData` | **shipyardGroup.userData.procTreeInstMeshes** | `allTreeInstMeshes.slice();` |
| [`L28943`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28943) | `userData` | **shipyardGroup.userData.blenderForestPlacements** | `{` |
| [`L28978`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28978) | `userData` | **shipyardGroup.userData.treeShadowInstMesh** | `_syTreeShadInst;` |
| [`L28981`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28981) | `userData` | **shipyardGroup.userData.forestTrunksInstMesh** | `forestTrunksInstMesh;` |
| [`L28982`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28982) | `userData` | **shipyardGroup.userData.allTreeInstMeshes** | `allTreeInstMeshes;` |
| [`L29252`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29252) | `Abschnitt` | **1. Bäume: Echtes 4-Stufen-LOD (Desktop: 150m / 500m / 1500m / 3000m, Werft & Ararat!)** | `` |
| [`L29515`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29515) | `Abschnitt` | **2. Prüfe die Strauch-Meshes (shrubInstMeshes — bis 640 m & hartes Frustum-Culling)** | `` |
| [`L29566`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29566) | `Abschnitt` | **3. Hydrierte Blender-Unterholz-, Gras-/Schilf-, Agrar- & Tempelzierbotanik-Gruppen (Werft & Ararat + Frustum-Culling)** | `` |
| [`L29726`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29726) | `Abschnitt` | **4. Frustum- & Distanz-Culling für Werft-Handwerker (dryWorkers) & Stadtbewohner-Zone (Ur-Schinar)** | `` |
| [`L30682`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30682) | `Abschnitt` | **1. Sträucher & Euphrat-Schilf/Papyrus aus procShrubMeshes** | `` |
| [`L30711`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30711) | `Abschnitt` | **2. Steppengras & Hochgras aus blenderGrassSpecs** | `` |
| [`L30734`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30734) | `Abschnitt` | **3. Mesopotamische Kulturpflanzen & Weinreben aus blenderCropSpecs** | `` |
| [`L30755`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30755) | `Abschnitt` | **4. Tempel-, Hofgarten-, Terrakotta-Kübel- & Lotus-Zierbotanik** | `` |
| [`L30842`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30842) | `Abschnitt` | **1. Ararat-Bäume nach (species, stage, varIdx) bündeln & auf 4-LOD-Pools (150/500/1500/3000m) mappen** | `` |
| [`L31000`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31000) | `Abschnitt` | **2. Ararat Sträucher, Schilf & Pioniergras als LOD-gepoolte ExtraGroups (mit uSproutGrowth & Frustum-Culling)** | `` |
| [`L31164`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31164) | `Abschnitt` | **5. Kompletter Neuaufbau des Ararat-Landeplatzes (Arche.Environment.buildAraratLandingSite3D)** | `` |

### 4.2 Ararat-Landeplatz (`buildAraratLandingSite3D`)
> Bereich: **Zeile 31176 bis 33202** (Funktion `Arche.Environment.buildAraratLandingSite3D`)

| Zeile | Typ | Baugruppe / Eigenschaft | Details |
|:-----:|:---:|:------------------------|:--------|
| [`L31180`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31180) | `userData` | **araratGroup.userData.isBuilt** | `true;` |
| [`L31181`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31181) | `userData` | **araratGroup.userData.saddleMesh** | `null;` |
| [`L31182`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31182) | `userData` | **araratGroup.userData.altarCoals** | `null;` |
| [`L31183`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31183) | `userData` | **araratGroup.userData.disembarkRampMesh** | `null;` |
| [`L31195`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31195) | `userData` | **araratGroup.userData.heightMapTex** | `bakedAra.tex;` |
| [`L31198`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31198) | `Abschnitt` | **1. Integriertes Hochgebirgs- & Sattel-Mesh (1.400 x 1.400 m, 208 x 208 Segmente mit zentrierter Auflösungs-Verdichtung für glatte Gipfelgrate & bündigen Kielsattel)** | `` |
| [`L31226`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31226) | `userData` | **araratGroup.userData.saddleMesh** | `terrainMesh;` |
| [`L31253`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31253) | `userData` | **araratGroup.userData.horizonRingMesh** | `araHorizon.mesh;` |
| [`L31254`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31254) | `userData` | **araratGroup.userData.horizonMat** | `araHorizon.mat;` |
| [`L31320`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31320) | `userData` | **araratGroup.userData.basaltCragsInstMesh** | `cragInst;` |
| [`L31442`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31442) | `userData` | **araratGroup.userData.waterfallGroup** | `waterfallGroup;` |
| [`L31443`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31443) | `userData` | **araratGroup.userData.waterfallUniforms** | `waterfallUniforms;` |
| [`L31445`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31445) | `Abschnitt` | **2. Fels-, Holz-, Feuer- & Bronzezeit-Materialien (alle WebGL1 AAA-gekoppelt & Thermo-/Struktur-fähig)** | `` |
| [`L31504`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31504) | `Abschnitt` | **3. Ausschiffungs-Steg & 4-stufiger Baufortschritt (rampStages) mit Catenary-Hanfseilen & Zimmermannsholz** | `` |
| [`L31756`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31756) | `userData` | **araratGroup.userData.rampStages** | `{` |
| [`L31762`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31762) | `userData` | **araratGroup.userData.disembarkRampMesh** | `gangwayDeck;` |
| [`L31768`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31768) | `Abschnitt` | **4. Großer Zyklopischer Dankopfer-Altar (Gen 8,20 / Ex 20,25), Opferfeuer (~600°C Thermo) & Noahs gesamte Familie (8 Personen)** | `` |
| [`L31839`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31839) | `userData` | **araratGroup.userData.altarStoneGroup** | `altarStoneGroup;` |
| [`L31853`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31853) | `userData` | **araratGroup.userData.altarCoals** | `coalMesh;` |
| [`L31877`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31877) | `userData` | **araratGroup.userData.uAltarFireThermo** | `uAltarFireThermo;` |
| [`L31878`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31878) | `userData` | **araratGroup.userData.uAltarFlicker** | `uAltarFlicker;` |
| [`L31904`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31904) | `userData` | **araratGroup.userData.altarEmberGlow** | `altarEmberGlow;` |
| [`L31911`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31911) | `userData` | **araratGroup.userData.altarFlickerLight** | `altarFlickerLight;` |
| [`L31913`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31913) | `Abschnitt` | **1. Volumetrisches fBm-Schwarzkörper-Opferfeuer (7 gekreuzte Flammen-Flächen = 1 Draw-Call, WebGL1-konform)** | `` |
| [`L32036`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32036) | `userData` | **araratGroup.userData.altarFlames** | `altarFlames;` |
| [`L32038`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32038) | `Abschnitt` | **2. Aufsteigende Funken & Glut-Asche (45 Funken in 1 THREE.Points Draw-Call, rein im Shader animiert)** | `` |
| [`L32103`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32103) | `userData` | **araratGroup.userData.altarSparks** | `altarSparks;` |
| [`L32105`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32105) | `Abschnitt` | **3. Weicher prozeduraler Opferrauch (Noise-Alpha-Billboards, keine harten Kugel-Silhouetten!)** | `` |
| [`L32184`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32184) | `userData` | **araratGroup.userData.altarSmokePuffs** | `altarSmokePuffs;` |
| [`L32217`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32217) | `userData` | **araratGroup.userData.altarGroup** | `altarGroup;` |
| [`L32220`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32220) | `Abschnitt` | **5. Kreativ-Highlight: Bronzezeitliches Basislager am Stegfuß (Terrakotta-Amphoren, Zedernkiste, Werkzeuge, Hanftau — mat zuerst!)** | `` |
| [`L32276`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32276) | `userData` | **araratGroup.userData.campGroup** | `campGroup;` |
| [`L32299`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32299) | `userData` | **araratGroup.userData.svalbardPlotGroup** | `svalbardPlotGroup;` |
| [`L32302`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32302) | `Abschnitt` | **6. Kreativ-Highlight: Schimmernde Gletscher-Schmelzwasser-Tümpel & Südtal-Tränkelagunen** | `` |
| [`L32335`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32335) | `userData` | **araratGroup.userData.meltwaterGroup** | `meltwaterGroup;` |
| [`L32374`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32374) | `userData` | **araratGroup.userData.strandedMatsGroup** | `strandedMatsGroup;` |
| [`L32375`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32375) | `userData` | **araratGroup.userData.matCentersAra** | `matCentersAra;` |
| [`L32378`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32378) | `Abschnitt` | **7. Weiträumige Auswanderungs-Korridore & Herden-Verteilung über das gesamte Ararat-Massiv (Kap. 14.5)** | `` |
| [`L32524`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32524) | `userData` | **araratGroup.userData.plateauQuadInstMesh** | `plateauQuadInstMesh;` |
| [`L32525`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32525) | `userData` | **araratGroup.userData.plateauMovers** | `plateauMovers;` |
| [`L32526`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32526) | `userData` | **araratGroup.userData.plateauFaunaGroup** | `plateauFaunaGroup;` |
| [`L32529`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32529) | `Abschnitt` | **8. Kreativ-Highlight: Taube mit Ölzweig (0), Rabe (1) + 42-Vögel-Schwarm aus Himmelsdeck / Zohar in freier Bergthermik (Kap. 14.5 Phase 1)** | `` |
| [`L32569`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32569) | `userData` | **araratGroup.userData.avianFlyInstMesh** | `avianFlyInstMesh;` |
| [`L32603`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32603) | `userData` | **araratGroup.userData.doveSprigGroup** | `doveSprigGroup;` |
| [`L32610`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32610) | `userData` | **araratGroup.userData.doveHeroAnchor** | `doveHeroAnchor;` |
| [`L32625`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32625) | `Abschnitt` | **9. Kreativ-Highlight: Regenbogen-Bundesbogen hoch & weit am Himmel HINTER dem Ararat-Massiv (Gen 9,13, 0% Bergschnitt!)** | `` |
| [`L32685`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32685) | `userData` | **araratGroup.userData.rainbowArcMesh** | `rainbowArcMesh;` |
| [`L32686`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32686) | `userData` | **araratGroup.userData.rainbowUniforms** | `rainbowUniforms;` |
| [`L32690`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32690) | `userData` | **araratGroup.userData.impactFX** | `Arche.Fauna.createGroundImpactFX(araratGroup, 64, 56, true);` |
| [`L32858`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32858) | `userData` | **araratGroup.userData.sproutGrassMesh** | `araratSproutGrassInstMesh;` |
| [`L32861`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32861) | `Abschnitt` | **11. Echte botanische Werft-Vegetation + Ovoli-Olivenstümpfe & Schilf auf Ararat (Kap. 15.3–15.6)** | `` |
| [`L32978`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32978) | `userData` | **araratGroup.userData.procAraTreeMeshes** | `_procAraTreeMeshes;` |
| [`L32979`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32979) | `userData` | **araratGroup.userData.blenderAraratHydrated** | `false;` |
| [`L32980`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32980) | `userData` | **araratGroup.userData.blenderAraratSpecs** | `[` |
| [`L33041`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33041) | `userData` | **araratGroup.userData.procAraAllMeshes** | `floraInstMeshes.slice();` |
| [`L33042`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33042) | `userData` | **araratGroup.userData.blenderAraratSpecs** | `araratGroup.userData.blenderAraratSpecs.concat(araShrubSpecs);` |
| [`L33065`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33065) | `userData` | **araratGroup.userData.ovoliShootsGroup** | `ovoliShootsGroup;` |
| [`L33096`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33096) | `userData` | **araratGroup.userData.treeShadowInstMesh** | `_araTreeShadInst;` |
| [`L33100`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33100) | `userData` | **araratGroup.userData.oliveSaplingsGroup** | `araratOliveSaplingsGroup;` |
| [`L33101`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33101) | `userData` | **araratGroup.userData.floraInstMeshes** | `floraInstMeshes;` |
| [`L33102`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33102) | `userData` | **araratGroup.userData.oliveSaplings** | `[];` |
| [`L33103`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33103) | `userData` | **araratGroup.userData.themedMats** | `themedMatsAra;` |
| [`L33108`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33108) | `Abschnitt` | **3. Exakte Höhen-Synchronisation & Ausblenden des schwarzen seaGrid** | `` |

---

## 5. Modul- & Top-Level-Funktionen

### 5.1 Arche.Procedural (Texturen, POM & Shader)

| Zeile | Funktion / Signatur |
|:-----:|:--------------------|
| [`L5184`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5184) | `Arche.Procedural.createInstantPlaceholderTex(r, g, b, repU = 1.0, repV = 1.0)` |
| [`L5364`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5364) | `Arche.Procedural.spawnMulticoreTexturePool()` |
| [`L5490`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5490) | `Arche.Procedural.buildWaterNormalTexture()` |
| [`L5527`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5527) | `Arche.Procedural.buildRoughnessTexture()` |
| [`L5569`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5569) | `Arche.Procedural.bindInteriorLightUniforms(shader)` |
| [`L5648`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5648) | `Arche.Procedural.attachCloseUpDetailLOD(mat, isPitchHull = false, isBarrelMat = false, isVolumetricBedding = false, isBasaltStone = false)` |
| [`L6036`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6036) | `Arche.Procedural.bindGpuShader(material, fixedMatId = 1)` |
| [`L6210`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6210) | `Arche.Procedural.bindEnvUniforms(shader)` |
| [`L6218`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6218) | `Arche.Procedural.injectEnvFogAndCloud(fragShader, worldPosExpr, applyCloudShadow = true, horizonShadowExpr = '')` |
| [`L6246`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6246) | `Arche.Procedural.bindMechPomShader(colorHex, mechType = 1)` |
| [`L6431`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6431) | `Arche.Procedural.cloneNoDeckClipMat(srcMat)` |
| [`L9675`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9675) | `Arche.Procedural.buildBeddingAlphaShellTexture()` |
| [`L9760`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9760) | `Arche.Procedural.buildVerticalHayFinTexture()` |
| [`L13823`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L13823) | `Arche.Procedural.updateInstancedBarrelsShader(ctx)` |
| [`L14722`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L14722) | `Arche.Procedural.updateDrivetrainAndGalleyVisuals(ctx, fixRes, shiftState)` |
| [`L18174`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18174) | `Arche.Procedural.updateStormShutters3D(v_roof_kmh, mu_wind_rad, precip_mmh, ctx)` |
| [`L21317`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21317) | `Arche.Procedural.makeEnvMat(cacheKey, baseHex, rough, metal, fragExtraGLSL, options = {})` |
| [`L36544`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36544) | `Arche.Procedural.rebuildAirflow3DGeometry()` |
| [`L40068`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40068) | `Arche.Procedural.tempToHeatmapRGB(tempC)` |

### 5.2 Arche.Environment (Werft, Ararat & Botanik)

| Zeile | Funktion / Signatur |
|:-----:|:--------------------|
| [`L6756`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6756) | `Arche.Environment.loadTerrainTextures()` |
| [`L9965`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9965) | `Arche.Environment.heightTexUniforms(()` |
| [`L18295`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18295) | `Arche.Environment.updateDeckSlicePlaneWorld()` |
| [`L18955`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18955) | `Arche.Environment.createZUpCylinderGeo(rTop, rBot, heightZ, segs = 12)` |
| [`L18962`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18962) | `Arche.Environment.addStrutBetweenPoints(parentGroup, p0, p1, rBot = 0.12, rTop = 0.12, mat = null, tooltipKey = null)` |
| [`L19019`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19019) | `Arche.Environment.evalRiverCenterX(y)` |
| [`L19025`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19025) | `Arche.Environment.evalRiverHalfWidth(y)` |
| [`L19030`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19030) | `Arche.Environment.evalRiverSurfaceZ(y)` |
| [`L19038`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19038) | `Arche.Environment.evalApproachRoadX(y)` |
| [`L19075`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19075) | `Arche.Environment.evalLakeLobeRadiusFrac(lake, x, y)` |
| [`L19085`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19085) | `Arche.Environment.evalLakeShorePoint(lake, ang, rFrac = 1.0)` |
| [`L19093`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19093) | `Arche.Environment.evalAlluvialLakeField(x, y)` |
| [`L19103`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19103) | `Arche.Environment.evalDistToPolyline(x, y, pts)` |
| [`L19117`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19117) | `Arche.Environment.evalCanalField(x, y)` |
| [`L19141`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19141) | `Arche.Environment.evalShipyardTerrainZ(x, y)` |
| [`L19286`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19286) | `Arche.Environment.evalAraratTerrainZ(x, y)` |
| [`L19879`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19879) | `Arche.Environment.getOrientalFoliageAtlasTex()` |
| [`L20089`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20089) | `Arche.Environment.pushLimb(buf, p0, p1, r0, r1, nSegs, rCol, gCol, bCol)` |
| [`L20147`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20147) | `Arche.Environment.pushFoliageCluster(buf, cx, cy, cz, rx, ry, rz, quadIdx, rCol, gCol, bCol, nCards = 9)` |
| [`L20206`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20206) | `Arche.Environment.pushPalmFrondRibbon(buf, spinePts, wStart, wMax, wEnd, rCol, gCol, bCol)` |
| [`L20268`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20268) | `Arche.Environment.createOrientalTreeGeo(speciesIdx, variantIdx)` |
| [`L20628`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20628) | `Arche.Environment.createOrientalShrubGeo(shrubType)` |
| [`L20722`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20722) | `Arche.Environment.getBotanyThicknessTex()` |
| [`L20749`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20749) | `Arche.Environment.applyOrientalFoliageShader(mat, options = {})` |
| [`L21524`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21524) | `Arche.Environment.createHorizonTerrainRing(opts)` |
| [`L21642`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21642) | `Arche.Environment.bakeTerrainHeightTex(evalLocalZFn, halfSpan = 3000.0, res = 256)` |
| [`L21678`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21678) | `Arche.Environment.getTreeShadowBlobTex()` |
| [`L21723`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21723) | `Arche.Environment.createProjectedTreeShadowsMesh(treesList, evalTerrainZFn, opts = {})` |
| [`L21873`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21873) | `Arche.Environment.createProjectedBuildingShadowsMesh(bldgBoxes, evalTerrainZFn, opts = {})` |
| [`L21995`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21995) | `Arche.Environment.evalShipyardHorizonZ(wx, wy, uRadOpt, isSkirtOpt)` |
| [`L22020`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22020) | `Arche.Environment.evalAraratHorizonZ(wx, wy, uRadOpt, isSkirtOpt)` |
| [`L22047`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22047) | `Arche.Environment.buildShipyard3D()` |
| [`L29032`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29032) | `Arche.Environment.updateVegetationLOD(cam, forceUpdate = false)` |
| [`L30111`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30111) | `Arche.Environment.registerBotanySpecies(speciesKey, opts = {})` |
| [`L30116`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30116) | `Arche.Environment.loadBotanyPlantPack(speciesKey, glbUrl, opts = {})` |
| [`L30130`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30130) | `Arche.Environment.applyBotanyShaderToObject(rootObj, opts = {})` |
| [`L30171`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30171) | `Arche.Environment.loadBlenderBotanyPacks()` |
| [`L30231`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30231) | `Arche.Environment._mergeShadowProxyGeo(parts)` |
| [`L30271`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30271) | `Arche.Environment._allocTreeShadowProxyPool(cap, archKey, refSp, packsMap, parentGrp, poolList, poolMap, meshAcc, tooltipKey, depthMat, namePrefix)` |
| [`L30309`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30309) | `Arche.Environment.hydrateBlenderForest3D(packsMap)` |
| [`L30545`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30545) | `Arche.Environment.hydrateBlenderExtraBotany3D(packsMap)` |
| [`L30783`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30783) | `Arche.Environment.hydrateBlenderAraratFlora3D(packsMap)` |
| [`L31150`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31150) | `Arche.Environment.hydrateBlenderBotany3D()` |
| [`L31166`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31166) | `Arche.Environment.ensureAraratBuilt()` |
| [`L31176`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31176) | `Arche.Environment.buildAraratLandingSite3D()` |
| [`L33116`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33116) | `Arche.Environment.evalShipyardAbsTerrainZ(x, y)` |
| [`L33120`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33120) | `Arche.Environment.evalAraratAbsTerrainZ(x, y)` |
| [`L33125`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33125) | `Arche.Environment.evalTerrainBaseAbsNN(day)` |
| [`L33136`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33136) | `Arche.Environment.evalWaterLevelAbsNN(day)` |
| [`L33182`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33182) | `Arche.Environment.evalAbsoluteElevationCouple(wAbsNN, siteBaseNN, T_mean, hExtKeel)` |
| [`L33195`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33195) | `Arche.Environment.evalWaterRiseOffset(depth, T_mean, wAbsOverride, siteBaseOverride)` |
| [`L33203`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33203) | `Arche.Environment.updateLandmarksAndTerrain3D(depth, T_mean, dynHeaveZ, isThermalMode, isTexturedMode)` |
| [`L34977`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34977) | `Arche.Environment.updateFloatingMats3D(depth, waterRiseOffset, simTime, k, k_x, k_y, halfH, phi_rad, omega, wModel, mu_wind_rad, v_wind_ms, matsFrac, showWat)` |
| [`L43652`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43652) | `Arche.Environment.updateHullWaterFilm3D(depth, dt_sim, isThermalMode)` |

### 5.3 Arche.Fauna (Organische Tiere, Ochsen & Knechte)

| Zeile | Funktion / Signatur |
|:-----:|:--------------------|
| [`L14895`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L14895) | `Arche.Fauna.subdivideCatmullPts(pts, subdiv = 2)` |
| [`L14919`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L14919) | `Arche.Fauna.buildOrganicLoftGeometry(tubes, radSegs = 20, subdiv = 2)` |
| [`L14986`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L14986) | `Arche.Fauna.buildPbrMaps()` |
| [`L15048`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15048) | `Arche.Fauna.getMorphTypeForGenusId(genusId)` |
| [`L15067`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15067) | `Arche.Fauna.getFaunaBoardingHeaderGLSL(isDepthPass = false)` |
| [`L15258`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15258) | `Arche.Fauna.getFaunaNormalDeformGLSL(archetypeMode = 'QUAD')` |
| [`L15325`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15325) | `Arche.Fauna.getFaunaVertexDeformGLSL(archetypeMode = 'QUAD', isDepthPass = false)` |
| [`L15827`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15827) | `Arche.Fauna.createFaunaDepthMaterial(archetypeMode = 'QUAD', locoScaleUniform = null)` |
| [`L15858`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15858) | `Arche.Fauna.createFaunaMaterial(rough = 0.62, baseHex = 0xffffff, coatClass = 'FUR', archetypeMode = 'QUAD')` |
| [`L16073`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16073) | `Arche.Fauna.createGroundImpactFX(parentGroup, maxPuffs = 64, maxRings = 56, isBasalt = false)` |
| [`L16235`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16235) | `Arche.Fauna.buildSculptedLimb(xHip, yHip, zHip, lenZ, rTop, rKnee, rHoof, cHide, isHind = false)` |
| [`L16249`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16249) | `Arche.Fauna.addHeadDetails(tubes, yEye, zEye, wHead, yEar, zEar, earW, earL, cIvory, hornType = 'BOVINE')` |
| [`L16301`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16301) | `Arche.Fauna.initArchetypesAndGoepelOxen()` |
| [`L16677`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16677) | `Arche.Fauna.getGenusInfo(genusId)` |
| [`L16712`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16712) | `Arche.Fauna.populateAllDecks()` |
| [`L17260`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17260) | `Arche.Fauna.resolveCollisionsAndClearCorridors()` |
| [`L17527`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17527) | `Arche.Fauna.syncVisibilityAndClip(zSliceMax)` |
| [`L17535`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17535) | `Arche.Fauna.updateShaderAndColors(ctx)` |
| [`L39036`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39036) | `Arche.Fauna.getIndividualHoverTooltip(ttKey, localPt, mode)` |

### 5.4 Arche.Physics (Wellen, Ozean, Mikroklima & Schichtpläne)

| Zeile | Funktion / Signatur |
|:-----:|:--------------------|
| [`L14558`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L14558) | `Arche.Physics.evaluateGoepelShiftSchedule(timeOfDayHrs, isScheduleActive = false, overrideMode = null)` |
| [`L14590`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L14590) | `Arche.Physics.evaluateArkTaxonomicCensus(payloadFrac = 1.0)` |
| [`L18104`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18104) | `Arche.Physics.evaluateShutterAerodynamics(headModeStr, v_roof_ms, rho_air, precip_mmh, isFullShipZohar = true, isBadgirActive = true, out = _shutterAeroScratch)` |
| [`L45804`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45804) | `Arche.Physics.evalWorldGroundSDF(wx, wy, wz)` |
| [`L45980`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45980) | `Arche.Physics.sampleMicroclimateAt(xShip, yShip, zShip, out = _microclimateScratch)` |
| [`L46066`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46066) | `Arche.Physics.evaluateAirflowVelocityField(xShip, yShip, zShip, out = _airflowVelScratch)` |

### 5.5 Arche.Performance & Quality-Governor

*Keine direkten Funktionsdeklarationen in dieser Sektion.*

### 5.6 Arche.UI & Bilinguale Tooltips

| Zeile | Funktion / Signatur |
|:-----:|:--------------------|
| [`L39168`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39168) | `Arche.UI.get3DHoverTooltipByMode(ttKey, localPt, overrideShaderMode = null)` |
| [`L39626`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39626) | `Arche.UI.getTooltip(key, lang = params.language, mode = Arche.State.viewShader, localPt = null)` |

### 5.7 Arche.Player & Kamera-Steuerung

| Zeile | Funktion / Signatur |
|:-----:|:--------------------|
| [`L45838`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45838) | `Arche.Player.flyTo(posArr, targetArr, durationSec = 1.25)` |
| [`L45853`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45853) | `Arche.Player.updateCameraAndLabels()` |

### 5.8 Top-Level Engine- & Lifecycle-Funktionen

| Zeile | Funktion / Signatur |
|:-----:|:--------------------|
| [`L2193`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2193) | `toggleBox(contentId, btnId)` |
| [`L2201`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2201) | `toggleMainTelemetryPanel()` |
| [`L2223`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2223) | `initMobileCamDpad()` |
| [`L2352`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2352) | `getDeckZ(kIdx, yVal)` |
| [`L2407`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2407) | `buildWoodMaterial(spec)` |
| [`L2472`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2472) | `getWoodMat(key)` |
| [`L2483`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2483) | `handsToM(val)` |
| [`L2486`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2486) | `handsToCm(val)` |
| [`L2489`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2489) | `toHandsVal(val)` |
| [`L2492`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2492) | `zoharSpacingToM(val)` |
| [`L2495`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2495) | `badgirHeightToM(val)` |
| [`L2498`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2498) | `isZoharFullShipExtent(modeStr)` |
| [`L2502`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2502) | `computeStructuralComponentMasses()` |
| [`L3166`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L3166) | `getDynamicDashboardTooltip(key)` |
| [`L4482`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L4482) | `getWoodTooltipHelper(propKey, labelDE, labelEN, roleDE, roleEN)` |
| [`L4504`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L4504) | `getDynamicGuiTooltip(ctrlKeyOrName)` |
| [`L5171`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5171) | `cpuNoise2D(x, y)` |
| [`L5230`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5230) | `fastNoise2D(x, y)` |
| [`L5243`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5243) | `generateAlbedo(typeId)` |
| [`L5334`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5334) | `generateNormal(normId)` |
| [`L5408`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5408) | `applyFinishedJob(res)` |
| [`L5442`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5442) | `triggerMainThreadFallback()` |
| [`L5447`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5447) | `stepNextFallbackJob()` |
| [`L6440`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6440) | `orientCylinderUVsAlongAxis(geo, lengthM, radiusM)` |
| [`L6453`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6453) | `mergeTransformedGeos(entries)` |
| [`L6511`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6511) | `mergeRigidChildrenByMaterial(grp, excludeSet = null)` |
| [`L6563`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6563) | `createLanternPinionMesh(radius, length, nStaves, axis, diskMat, staveMat)` |
| [`L6592`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6592) | `createCrownWheelMesh(radius, rimThick, nTeeth, axis, toothSign, rimMat, toothMat)` |
| [`L6622`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6622) | `createArchimedeanHelixGeometry(rInner, rOuter, length, nTurns, radialSegs = 180)` |
| [`L6650`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6650) | `createWoodenDogClutchGroup(axis, hornbeamMat, oakMat)` |
| [`L8123`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8123) | `hasGLTFLoader()` |
| [`L8127`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8127) | `_getGLTFLoader(options)` |
| [`L8147`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8147) | `_isFileProtocol()` |
| [`L8151`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8151) | `_decodeBundleEntry(entry)` |
| [`L8171`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8171) | `_computeAssetModeColor(mat, viewShader, tEnv)` |
| [`L8187`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8187) | `attachArcheMaterialHooks(mat, options = {})` |
| [`L8408`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8408) | `syncViewShader(viewShader, tEnv)` |
| [`L8422`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8422) | `_parseGLTFBuffer(loader, arrayBuffer, resourcePath)` |
| [`L8437`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8437) | `_loadRawGLTFScene(slotKey, url, options = {})` |
| [`L8475`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8475) | `_applyTransformOpt(vec3Obj, val)` |
| [`L8482`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8482) | `_findManifestMeta(slotKey)` |
| [`L8497`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8497) | `loadGLBSlot(slotKey, url, targetParent, options = {})` |
| [`L8627`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8627) | `_isPlaceholderAlive(placeholder)` |
| [`L8637`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8637) | `_pruneStaleTargets(slotKey)` |
| [`L8651`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8651) | `_tryMountTarget(entry)` |
| [`L8736`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8736) | `registerReplaceTarget(slotKey, proceduralPlaceholderGroup, mountConfig = {})` |
| [`L8763`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8763) | `restoreProceduralFallback(slotKey)` |
| [`L8785`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8785) | `mountAllRegisteredSlots()` |
| [`L8798`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8798) | `initManifest(manifestUrl = 'assets/manifest.json')` |
| [`L8818`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8818) | `getStatus()` |
| [`L8837`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8837) | `extractInstancedTemplate(glbScene, options = {})` |
| [`L8896`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8896) | `createInstancedMesh(templateOrScene, maxCount, options = {})` |
| [`L8934`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8934) | `registerManagedMaterial(mat, options = {})` |
| [`L8957`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8957) | `configureSmoothLODGroup(lodGroup, opts = {})` |
| [`L11188`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11188) | `createLayerBucket()` |
| [`L11199`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11199) | `woodKeyToTexIdx(woodKey)` |
| [`L11206`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11206) | `resolvePartDynamicTexIdx(bucket, x, y, z, nx, ny, nz, elemType, matType, fixTag, forceTexIdx)` |
| [`L11250`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11250) | `addQuadToBucket(bucket, p1, p2, p3, p1_dup, p3_dup, p4, nx, ny, nz, elemType, matType, fixTag = 0,...)` |
| [`L11299`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11299) | `refreshAllWoodMaterialGroups()` |
| [`L11335`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11335) | `addBoxToBucket(bucket, x0, x1, y0, y1, z0, z1, elemType, matType, fixTag = 0, forceTexIdx = -1)` |
| [`L11343`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11343) | `addThickQuadToBucket(bucket, p1, p2, p3, p4, dx, dy, dz, nx, ny, nz, elemType, matType, fixTag = 0)` |
| [`L11360`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11360) | `addStormShutterInstance(xShip, yShip, zHinge, spanW, chordH, sideDir, isBadgirFlap = false)` |
| [`L11372`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11372) | `addHorizontalBarrelCylinderRow(bucket, wireArr, x0, x1, yCenter, zCenter, radius, nSegs, fixTag = 3)` |
| [`L11378`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11378) | `addBoneTimberInstance(x0, y0, z0, x1, y1, z1, radius)` |
| [`L11388`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11388) | `addVolumetricBeddingZone(x0, x1, y0, y1, zBase, thicknessZ, moundPeakZ = 0.0, densityWeight = 1.0)` |
| [`L11397`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11397) | `buildVolumetricHullWallsAndDecks()` |
| [`L11421`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11421) | `addDeckBayWithCutout(x0, x1, y0, y1, z0, z1, cX0, cX1, cY0, cY1, matType, addGuardrail = false, openXSi...)` |
| [`L12028`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12028) | `addWireBox(x0, x1, y0, y1, z0, z1)` |
| [`L12266`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12266) | `addBarrelPerpendicularToWallY(bucket, wireArr, xCenter, y0, y1, zCenter, radius, nSegs, fixTag = 3, cutawayHide ...)` |
| [`L12283`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12283) | `addTransverseBulkheadBarrelRack(xR0, xR1, yRack0, yRack1, zKantTop, zDeck, rowCountsZ, forceColsY = 0)` |
| [`L12313`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12313) | `addChineWallBarrelRack(xCh0, xCh1, yCh0, yCh1, zDeck, isPortSide, nColsX = 5, nRowsY = 2)` |
| [`L12373`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12373) | `addDeck1MegafaunaStallRow(xM0, xM1, yBack, yFront, nStalls)` |
| [`L12457`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12457) | `addFlushChuteSlottedOakGrating3D(xG0, xG1, yC0, yC1, zDeck)` |
| [`L12471`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12471) | `addOpenFlushChute3D(x0, x1, y0, y1, zDeck)` |
| [`L12680`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12680) | `addDeck2AnimalPenRow(xP0, xP1, yBack, yFront, nPens)` |
| [`L12888`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12888) | `addDeck3AviaryBlock(xA0, xA1, y0, y1, nCages)` |
| [`L12973`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12973) | `addDeck3RodentHoneycombBlock(xR0, xR1, yShelf, nCols, halfDepthY = 0.38)` |
| [`L13526`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L13526) | `buildGeometryMaterialGroups(geo, metaList)` |
| [`L13730`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L13730) | `pushBedShellQuad(p1, p2, p3, p4, u0, v0, u1, v1, hLay0, hLay1 = hLay0)` |
| [`L13939`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L13939) | `createGoepelWheelGroup(xCenter)` |
| [`L14423`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L14423) | `createAnimatedPaternosterGroup(xCenter)` |
| [`L14542`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L14542) | `updatePaternosterAnimation(pGroup, liftPhase)` |
| [`L14603`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L14603) | `setDogClutchVisualState(clutchGrp, engaged)` |
| [`L14615`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L14615) | `updateGoepelTransmissionKinematics(gMaster, deltaAngleRad, shiftState = null)` |
| [`L17655`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17655) | `writeSiloConeCell(cellIdx, x0, x1, y0, y1, zE00, zE10, zE11, zE01, xM, yM, zApex, rA, gA, bA, rE, gE...)` |
| [`L17680`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17680) | `writeTkWatQuad(qIdx, p1x, p1y, p1z, p2x, p2y, p2z, p3x, p3y, p3z, p4x, p4y, p4z, nx, ny, nz, rT, ...)` |
| [`L17708`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17708) | `updateSiloGrainAndHighTanks3D(H_silo_fill_m, d3TankFillFrac, d2SpuelFillFrac, rollRad, pitchRad, isThermalMode, ...)` |
| [`L17798`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17798) | `buildSloshingTankVolume(x0, x1, y0, y1, zBot, zMeanWat, rTop, gTop, bTop, rBot, gBot, bBot, phaseOff)` |
| [`L17913`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17913) | `writeBilgeQuad(qIdx, p1x, p1y, p1z, p2x, p2y, p2z, p3x, p3y, p3z, p4x, p4y, p4z, nx, ny, nz, rT, ...)` |
| [`L17933`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17933) | `getDoubleBottomChamberType(iSec, jBay)` |
| [`L17944`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17944) | `updateBilgeWater3D(h_bilge_eff, rollRad, pitchRad, isThermalMode, T_bilge_C, T_sea_C)` |
| [`L18052`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18052) | `pushShutterBox(x0, x1, y0, y1, z0, z1, uScale = 1.0, vScale = 1.0)` |
| [`L18310`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18310) | `updateLayerVisibilities()` |
| [`L18492`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18492) | `writeVolRestQuad(posArr, colArr, quadIdx, xA, yA, xB, yB, rTop, gTop, bTop, rBot, gBot, bBot)` |
| [`L18753`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18753) | `spawnSplashParticle(wx, wy, wz, vx, vy, vz, pSize = 1.6, lifeDur = 1.0, jitterXY = 1.6)` |
| [`L18917`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18917) | `updateGate3D(mode)` |
| [`L19422`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19422) | `createGrassTuftGeo(h = 0.40, nBlades = 5, wBase = 0.12, wTop = 0.035)` |
| [`L19451`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19451) | `createShrubClusterGeo()` |
| [`L19495`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19495) | `createStaticGeometryBatcher()` |
| [`L19498`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19498) | `getBuffers(mat)` |
| [`L19507`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19507) | `addBox(mat, cx, cy, cz, sx, sy, sz, rx = 0, ry = 0, rz = 0)` |
| [`L19514`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19514) | `rotXform(x, y, z)` |
| [`L19524`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19524) | `rotNorm(nx, ny, nz)` |
| [`L19556`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19556) | `addStrut(mat, p0, p1, rTop, rBot, nSegs = 6)` |
| [`L19605`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19605) | `addCatenaryRope(mat, p0, p1, radius = 0.02, sagM = 0.14, nSteps = 12, nRadSegs = 6, windAmp = 0.035)` |
| [`L19702`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19702) | `addTentClothPanel(mat, cx, cy, cz, widthX, slopeL, rotX, nSegX = 12, nSegY = 6, rotZ = 0.0)` |
| [`L19710`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19710) | `evalPt(u, v)` |
| [`L19731`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19731) | `addGeometry(mat, srcGeo, matrix = null)` |
| [`L19759`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19759) | `buildMeshes(parentGroup, tooltipKey = null, opts = {})` |
| [`L19786`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19786) | `buildChunkedMeshes(parentGroup, tooltipKey = null, opts = {})` |
| [`L20188`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20188) | `calcNorm(px, py, pz)` |
| [`L22135`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22135) | `makeShipyardEnvMat(cacheKey, baseHex, rough, metal, fragExtraGLSL, options = {})` |
| [`L22673`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22673) | `nextRandC()` |
| [`L23398`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23398) | `nextRandVar()` |
| [`L24622`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24622) | `addAquaWater(geo, px, py, pz, rx = 0, quat = null)` |
| [`L24919`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24919) | `rotXY(cx, cy, lx, ly, yaw)` |
| [`L24923`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24923) | `addVillageSmoke(ox, oy, oz, pIdx)` |
| [`L24928`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24928) | `addMudbrickHouse(cx, cy, w, d, hWall, yaw, hasAwning, hasLadder, idx)` |
| [`L25318`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25318) | `addUrCourtyardHouse(cx, cy, w, d, h1, h2, yaw, awMat, hasOven, idx, targetBatch = cityBatch)` |
| [`L25337`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25337) | `addWingRoof(wx, wy, ww, wd, wh, addVigas)` |
| [`L25426`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25426) | `addUrInsula(cx, cy, totW, totD, cols, rows, yaw, seedOff, targetBatch = cityBatch)` |
| [`L25448`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25448) | `addUrCityGate(gx, gy, outYaw)` |
| [`L25514`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25514) | `addWallSpan(x0, y0, x1, y1, hWall, thick, hasCrenels = true)` |
| [`L25752`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25752) | `pushRoadTri(ax, ay, az, au, av, bx, by, bz, bu, bv, cx, cy, cz, cu, cv)` |
| [`L25756`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25756) | `addFlagstoneRoad(pts, width, tier = 0)` |
| [`L26017`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26017) | `appendCarvedCanalRibbon(pts, halfW, startExt = 0.0, endExt = 0.0, zStart = zCanalW, zEnd = zCanalW, watPts...)` |
| [`L26018`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26018) | `buildDensePath(srcPts)` |
| [`L26286`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26286) | `addRiverIntakeSluice(ix, iy, dirToLandX, zWat, spanHalf = 3.3)` |
| [`L26414`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26414) | `addMagurBoatSlot(hasLogs, x, y, z, yawZ, boatInfo)` |
| [`L26526`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26526) | `addCanalArchBridge(bx, by, yaw, spanW = 10.6, roadW = 4.2)` |
| [`L26542`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26542) | `addTimberJetty(jx, jy, yaw, len = 10.5, zWater = 0.80)` |
| [`L26559`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26559) | `addGrainSilo(sx, sy, rad = 2.35, h = 4.4)` |
| [`L26567`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26567) | `addMudhifHut(mx, my, yaw, len = 7.2, wid = 3.8)` |
| [`L26585`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26585) | `addTownKiln(kx, ky, smokeIdx)` |
| [`L26723`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26723) | `evalRegionalRoadDist(px, py)` |
| [`L26735`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26735) | `isSafeAgriSpot(wx, wy, minRoadDist = 5.0)` |
| [`L26827`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26827) | `addUprightStrawRick(fx, fy, fIdx, withThreshFloor)` |
| [`L26861`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26861) | `addFieldShelter(sx, sy, yaw)` |
| [`L26974`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26974) | `nextRandCrop()` |
| [`L27374`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27374) | `addCanalWeir(wx, wy, yaw, spanW = 6.4, zWater = 0.82)` |
| [`L27776`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27776) | `isShipyardWorkZone(x, y, pad = 0.0, forTrees = false)` |
| [`L28115`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28115) | `nextRandG()` |
| [`L28185`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28185) | `nextRandS()` |
| [`L28399`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28399) | `nextRandSt()` |
| [`L28515`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28515) | `nextRandT()` |
| [`L29798`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29798) | `_loadSharedBotanyTextures()` |
| [`L29885`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29885) | `_prepTexForBotany(tex, isColor, repeatWrap)` |
| [`L29898`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29898) | `_adaptBotanyMaterial(species, srcMat, isFol, sharedTex, opts = {})` |
| [`L29968`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29968) | `_extractSpeciesPack(species, glbScene, sharedTex, opts = {})` |
| [`L32803`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32803) | `nextRandSp()` |
| [`L32879`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32879) | `nextRandSap()` |
| [`L35180`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35180) | `getDeviceClass()` |
| [`L35192`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35192) | `detectInitialTier()` |
| [`L35224`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35224) | `resolveTierFromMode(pMode)` |
| [`L35234`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35234) | `applyTier(tierIdx, force = false)` |
| [`L35292`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35292) | `resetGovernorClock()` |
| [`L35300`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35300) | `tickGovernor(nowMs)` |
| [`L35357`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35357) | `getCurrentSpec()` |
| [`L35361`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35361) | `setProfileMode(modeStr)` |
| [`L35372`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35372) | `init()` |
| [`L35380`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35380) | `restoreStandardVisibilities()` |
| [`L35420`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35420) | `updateExteriorPortalCulling(cam)` |
| [`L35569`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35569) | `updateLegendMode(mode)` |
| [`L35698`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35698) | `updateScenarioDescription(scenName)` |
| [`L36007`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36007) | `translateGUI(lang)` |
| [`L36038`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36038) | `translateDOM(lang)` |
| [`L36260`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36260) | `showExpeditionBriefing()` |
| [`L36267`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36267) | `hideExpeditionBriefing()` |
| [`L36274`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36274) | `selectAppModeAndStart(mode)` |
| [`L36307`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36307) | `toggleLabExpeditionMode()` |
| [`L36316`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36316) | `reopenOnboardingModal(directBriefing = false)` |
| [`L36323`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36323) | `toggleLanguage(forceLang)` |
| [`L36520`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36520) | `getBadgirPairStationsX(count)` |
| [`L36528`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36528) | `updateBucketMeshGeometry(bucket)` |
| [`L36562`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36562) | `addPath(fn, pathType)` |
| [`L36584`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36584) | `bezier3(p0, p1, p2, p3, u)` |
| [`L36921`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36921) | `updateZoharAndBadgirGeometry()` |
| [`L37170`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37170) | `computeBadgirMassTons()` |
| [`L37203`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37203) | `resetWaveAndShipState()` |
| [`L37459`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37459) | `triggerPauseEquilibriumRelax()` |
| [`L37463`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37463) | `markCustomPreset()` |
| [`L37520`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37520) | `syncQuickViewDock()` |
| [`L37536`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37536) | `toggleQuickAirflow()` |
| [`L37542`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37542) | `setQuickShader(modeStr)` |
| [`L37548`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37548) | `setQuickSlice(sliceStr)` |
| [`L37554`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37554) | `setQuickWall(wallStr)` |
| [`L37588`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37588) | `enterArkInterior()` |
| [`L37605`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37605) | `flyToInteriorDeck(deckKey)` |
| [`L37632`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37632) | `updateInteriorNavHUD(forceNow = false)` |
| [`L37850`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37850) | `toggleHighlightTour()` |
| [`L37855`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37855) | `toggleFreeCameraMode(forceVal)` |
| [`L38035`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38035) | `applyPiersonMoskowitzWindSea(v_kmh)` |
| [`L38108`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38108) | `evaluateExpeditionLogistics(day, rain_mmh = 0.0, T_stall_C = 20.8, depth_m = 0.0, woodMoisturePct = 13.5, out ...)` |
| [`L38235`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38235) | `evaluateBiblicalChronicleState(day, instantSnap = false)` |
| [`L38636`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38636) | `syncChronicleUI()` |
| [`L38721`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38721) | `toggleChronicleVoyage()` |
| [`L38739`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38739) | `startPreFloodBunkering()` |
| [`L38754`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38754) | `resetVoyageToLand()` |
| [`L38768`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38768) | `changeChronicleSpeed(val)` |
| [`L38773`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38773) | `scrubChronicleDay(val)` |
| [`L38816`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38816) | `computeRawICDNodeKN(wallIdx, lvlIdx, stIdx)` |
| [`L38862`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38862) | `computeScaledICDNodeKN(wallIdx, lvlIdx, stIdx, precomputedRawSum = null)` |
| [`L38878`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38878) | `generateICDMarkdownReport()` |
| [`L38956`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38956) | `translateMarkdownReportEN(md)` |
| [`L38976`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38976) | `openICDModal()` |
| [`L38989`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38989) | `refreshICDMarkdown()` |
| [`L38997`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38997) | `closeICDModal()` |
| [`L39000`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39000) | `copyICDMarkdown()` |
| [`L39010`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39010) | `downloadICDMarkdown()` |
| [`L39023`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39023) | `getFixturePopularTooltip(key)` |
| [`L39638`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39638) | `renderActiveTooltipContent()` |
| [`L39655`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39655) | `showDynamicTooltip(source, key, clientX, clientY)` |
| [`L39665`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39665) | `positionSciTooltip(clientX, clientY)` |
| [`L39679`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39679) | `hideSciTooltip()` |
| [`L39711`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39711) | `resolve3DFixtureTooltipKey(hitObj, localPt, instanceId = undefined)` |
| [`L39850`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39850) | `_collectHoverTargets(node, out)` |
| [`L39869`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39869) | `perform3DRaycastInspect(clientX, clientY)` |
| [`L40001`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40001) | `computeUtilizationRGB(etaEC5, etaBruch, blinkState, outRGB)` |
| [`L40044`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40044) | `computeThermalRGB(tempC, outRGB)` |
| [`L40073`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40073) | `getBeaufortInfo(v_kmh)` |
| [`L40088`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40088) | `update3DLabel(mesh, domElem)` |
| [`L40101`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40101) | `getBarColor(etaEC5, etaBruch)` |
| [`L40108`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40108) | `computeHullSectionProperties(hasCrossBracing, hasHeavyPlanking, hasSwelling, tempInteriorC, effWaveHalfLen_m)` |
| [`L40263`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40263) | `evalWebES(z_upper)` |
| [`L40312`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40312) | `evalESRatio(z_val)` |
| [`L40373`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40373) | `evaluateOceanWave(x_ship, y_ship, k, k_x, k_y, halfH, phi_rad, omega, depth, waveModel, out)` |
| [`L40428`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40428) | `getStationEffectiveKNPerMeter(stIdx)` |
| [`L40449`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40449) | `evaluateICDWeightPerMeterMN(xs, totalWeightMN, payloadFrac)` |
| [`L40459`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40459) | `writeVolumeQuad(posArr, colArr, quadIdx, xA, yA, zTopA, rA, gA, bA, xB, yB, zTopB, rB, gB, bB, zFl...)` |
| [`L40474`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40474) | `writeFilmQuad(posArr, normArr, colArr, quadIdx, x0, y0, zBot0, zTop0, x1, y1, zBot1, zTop1, nx, ...)` |
| [`L40494`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40494) | `initOceanWaveWorker()` |
| [`L40500`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40500) | `evaluateExactHydrostatics(M_akt_t, V_ext_keels_m3, h_ext_keel_m, out = _maritimeScratch, rho_sea_override = ...)` |
| [`L40519`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40519) | `evaluateTransverseWaveFKFactor(k_y, B = B_SHIP)` |
| [`L40526`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40526) | `evaluateStripAddedMassAndSlam(subDraft, depth, geomSubDraft, draftBB_clean, draftSB_clean, vUpMid, vUpBB, vUpSB,...)` |
| [`L40557`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40557) | `stepSemiImplicitHeavePitch(heaveZ, heaveVel, heaveAcc, M11, C11, K11, pitchRad, pitchVel, pitchAcc, M22, C22,...)` |
| [`L40583`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40583) | `evaluateMetabolicHeatResponse(T_stall_C)` |
| [`L40593`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40593) | `evaluateBarnPhysiologyAndGasBalance(T_mean_C, RH_pct, T_bilge_C, Q_solar_roof_kW, Q_bio_total_kW, steamRate_kgh, V_dot...)` |
| [`L40700`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40700) | `evaluateAstronomyAndPsychrometrics(timeOfDay, latitude, cloudCover, extHumidity, precipIntensity, tAir, tWater, airPr...)` |
| [`L40815`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40815) | `evaluateCharnockWindAndSolAir(v_wind_10_kmh, H_wave, T_mean, badgirHeight, mu_wind_rad, rho_air, M_akt_t, GM_tra...)` |
| [`L40907`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40907) | `evaluateMassAndStabilityBalance(payloadPct, precipIntensity, dynRollRad, oxenBioEff, timeOfDay, out = _massStabScr...)` |
| [`L41090`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41090) | `evaluateThermalNetworkAndVentilation(T_current_C, prevRelHumidity, P_goepel_W, payloadFrac, waterDepth_m, T_mean, freeb...)` |
| [`L41210`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41210) | `evalStallHeatBalanceResidual(T_cand)` |
| [`L41452`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41452) | `evaluateDAlembertStripDynamics(k, k_x, k_y, halfH, phi_rad, omega, depth, wModel, mu_rad, T_mean, KG_height, M_ak...)` |
| [`L41739`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41739) | `evaluateRollAndSurgeSwayDynamics(dynamicMotion, autoPlay, dt_phys, halfH, depth, T_mean, BM_radius, KG_height, GM_t...)` |
| [`L41937`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41937) | `evaluateSideGateHydrostatics(gateMode, isSideGateOpen, zWaterAtGate, T_mean, dynHeaveZ, dynPitchRad, dynRollRad...)` |
| [`L42063`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42063) | `evaluateInternalFixturesMechanics(payloadFrac, oxenPresence, oxenBioEfficiency, H_wave, dynRollRad, dynPitchRad, dyn...)` |
| [`L42078`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42078) | `evalLocalG(x_m, y_m)` |
| [`L42558`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42558) | `evaluateHullHotspotsAndLUTs(payloadFrac, M_nutz_akt, m_roof_dyn, M_rain_roof_t, M_rain_soak_t, h_bilge_eff_m, ...)` |
| [`L42850`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42850) | `evaluateFatigueAndHotspotEC5(fatigueEnabled, chronicleActive, autoPlay, dt_phys, eqHoursStep, H_wave, omega, ma...)` |
| [`L42997`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42997) | `evaluate3DFieldPointMechanicsAndThermal(meta, isBadgirPart, isRoofPart, ctx = _shaderFrameCtx, out = _fieldPointScratch)` |
| [`L43464`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43464) | `evaluateVertexBufferColors(metaList, targetColArr, isBadgirPart, isRoofPart = false, ctx = _shaderFrameCtx)` |
| [`L43565`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43565) | `evaluateEC5AndNorris(sigma_glob, sigma_loc_bend, sigma_90_trans, tau_xy, matObj, isScarfLoc, d_member_m...)` |
| [`L44156`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44156) | `_initSSCS()` |
| [`L44302`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44302) | `_resizeSSCS()` |
| [`L44314`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44314) | `_isSSCSNearScene()` |
| [`L44334`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44334) | `_runSSCSContactPass()` |
| [`L44441`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44441) | `_compositeSSCSContactPass()` |
| [`L44451`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44451) | `animate(isSingleTestStep = false)` |
| [`L45908`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45908) | `syncMobileViewportAndPerf(isInit = false)` |
| [`L46170`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46170) | `runArcheUnitTests()` |
| [`L46179`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46179) | `assertTest(suite, name, condition, detailStr)` |
| [`L47493`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47493) | `openUnitTestModal(e)` |
| [`L47622`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47622) | `prewarmSimulationShaders()` |
| [`L47654`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47654) | `startArcheSimulationCleanly()` |


---

## 6. Vollständiges Unit-Test-Kataster (T01 bis T101)

> Ausgeführt durch `runArcheUnitTests()` (ab Zeile ~27436).  
> **Gesamt: 101 Tests** — 100% abgedeckt.

| ID | Zeile | Test-Suite | Test-Bezeichnung |
|:--:|:-----:|:-----------|:-----------------|
| **T01** | [`L46215`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46215) | 1. Ellen-Kanon, EN 338 & Clean Architecture | Biblische Hauptabmessungen (300 × 50 × 30 Ellen) |
| **T02** | [`L46220`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46220) | 1. Ellen-Kanon, EN 338 & Clean Architecture | 6–5–4–3-Handbreiten-Normquerschnitte (Glatte Handbreiten ohne cm-Rundung) |
| **T03** | [`L46225`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46225) | 1. Ellen-Kanon, EN 338 & Clean Architecture | EN 338 Fraktilmodul E_0,05 (Laubholz 0.84 vs. Nadelholz 0.67) |
| **T04** | [`L46231`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46231) | 1. Ellen-Kanon, EN 338 & Clean Architecture | EC5 Bemessungswerte f_d = f_k * k_mod / γ_M (NKL 3) |
| **T05** | [`L46235`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46235) | 1. Ellen-Kanon, EN 338 & Clean Architecture | 300-Knoten-ICD-Kataster Vollständigkeit & Symmetrie |
| **T06** | [`L46245`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46245) | 1. Ellen-Kanon, EN 338 & Clean Architecture | Glatte Ellen- & Handbreiten-Konsistenz (0,000 mm Zentimeter-Rundungsabweichung) |
| **T07** | [`L46256`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46256) | 1. Ellen-Kanon, EN 338 & Clean Architecture | Clean-Architecture-Registry (Arche.Groups & Arche.Materials), Basalt-Kombüse S7, Svalbard-Zeer & 0-ms-Schnittebene |
| **T08** | [`L46266`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46266) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Archimedisches Gleichgewicht T = (V_disp - V_Kiele) / (L*B*C_B) |
| **T09** | [`L46273`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46273) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Volumetrische Sensitivität V × ρ_EN338 (Sohle 5,0 Hände -> 6,5 Hände) |
| **T10** | [`L46277`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46277) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Metazentrische Anfangsstabilität GM_eff > 4.0 m |
| **T11** | [`L46281`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46281) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Freie-Oberflächen-Unterdrückung durch 7.500 Einzelfässer |
| **T12** | [`L46285`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46285) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | 3 Äußere Eichenkiele (Strandungs-Aufstandsfläche ≥ 350 m²) |
| **T13** | [`L46291`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46291) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Exakter Steiner-Formschwerpunkt KB & BM inkl. 3 Außenkiele |
| **T14** | [`L46303`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46303) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | D1-Fass-Wechselballast senkt KG, erhöht Tiefgang T & aufrichtendes Moment M·GM |
| **T15** | [`L46310`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46310) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Manning-Strickler-Regenwasseraufstau & Bilgenzulauf bei 1.200 mm/h Monsun |
| **T16** | [`L46316`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46316) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Kreiszylinder-Sehnenbreite b(h) = 2·√(R²-(h-R)²) maximiert |ΔGM| bei 50% Füllung |
| **T17** | [`L46322`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46322) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Flacher Bilgensumpf Pocket-Effekt dämpft freie Oberfläche bei starker Krängung |
| **T18** | [`L46343`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46343) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | 3D-Fass-Inventur (7.920 echte 8-Hände-Fässer) & 0 % Kollision (Silos, Schotttüren S1/14, Bâdgir-Schächte & Schnecken S4/11) |
| **T19** | [`L46352`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46352) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Miche-Flachwasser-Brecherlimit (H=20m bei d=12m begrenzt) |
| **T20** | [`L46359`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46359) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Stokes 3. Ordnung Kamm-Aufsteilung (η_Stokes > η_Sinus bei θ=0) |
| **T21** | [`L46365`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46365) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Wendel/Kim-Flachwasser-Quetschströmung (m'_add,flach > m'_add,tief) |
| **T22** | [`L46371`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46371) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Wagner/Ochi-Motter Keilslamming (Deadrise-Dämpfung bei φ=10° Krängung) |
| **T23** | [`L46377`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46377) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Analytischer Quer-Beugungsfaktor κ_trans(k_y*B) in Lang- vs. Kurzwelle |
| **T24** | [`L46383`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46383) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Unbedingte Stabilität des semi-impliziten Winkler-Felskontakt-Integrators |
| **T25** | [`L46390`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46390) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Nichtlineare Wall-Sided-Stabilität GZ(φ) > GM·sin(φ) bei φ = 15° |
| **T26** | [`L46401`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46401) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Ikeda-Kimmwirbeldämpfung B44_ikeda (Mittelkiel Y=0 + 2 Kimmkiele Y=±17.5 E.) |
| **T27** | [`L46405`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46405) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Vollständiger 6-DOF Roll-Trägheitstensor I_xx,tot (Struktur + ICD-Ladung + Added Mass) |
| **T28** | [`L46413`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46413) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | 2D-Beugungs-Surge (Auslöschung sinc(k_x·L/2) = 0 bei λ = L = 140 m vs. Langwelle) |
| **T29** | [`L46418`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46418) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Bodenkontakt-Arretierung (groundLock = 0 sperrt Surge/Sway bei Strandung) |
| **T30** | [`L46422`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46422) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Exakte Einzelpositionen (15 Längsgurte, 45 Stützen & 8 Bâdgire @ Y=±4.18m) in I_xx |
| **T31** | [`L46433`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46433) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Exakter Querkraft-Abschluss V_z(0) = 0 & V_z(140m) = 0 MN |
| **T32** | [`L46437`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46437) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Exakter Biegemoment-Abschluss M_y(0) = 0 & M_y(140m) = 0 MNm |
| **T33** | [`L46441`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46441) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Elastische 2-Knoten-Whipping-Eigenfrequenz f_1 im Zielband |
| **T34** | [`L46447`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46447) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | EC5 Anhang B (Möhler) — Wurzelknie erhöhen γ_mean & I_y,eff |
| **T35** | [`L46455`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46455) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | EC5 Gl. (6.17) — Exakt 100.0% bei σ_t,0,d = η_Schäft * f_t,0,d |
| **T36** | [`L46464`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46464) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | EC5 Gl. (6.19) — Quadratische Druck-Biege-Interaktion (u_c² + u_m) |
| **T37** | [`L46470`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46470) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | EC5 Gl. (6.23) — Biegeknicken (λ_rel > 0.30 -> k_c < 1.0 erhöht Ausnutzung) |
| **T38** | [`L46476`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46476) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | EC5 Gl. (3.1) — Höhenbeiwert k_h = (150/h)^0.2 für h < 150 mm |
| **T39** | [`L46482`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46482) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | 2D-Norris — Biaxiale Zug-Querdruck-Verschärfung (-u_0*u_90 > 0) |
| **T40** | [`L46486`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46486) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Johansen-Dübeltragfähigkeit (EC5 Gl. 8.6 & B.10) & Gustafsson k_v |
| **T41** | [`L46493`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46493) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Headless 2×2-D'Alembert-Löser schließt V_z(L), M_y(L) & M_t(L) exakt auf Null |
| **T42** | [`L46501`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46501) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | 3-Kiele-Winkler-Bodenkontakt erzeugt aufrichtendes Rollmoment (Y = ±17.5 E.) |
| **T43** | [`L46510`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46510) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Biaxiale Schrägbiegung (M_z), Vlasov-Wölbkrafttorsion & Racking-Schub in der 15×4-Hotspot-Suche |
| **T44** | [`L46521`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46521) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | 300-Knoten-Querdruck-LUT — 45 Eichen-Königsstützen senken Schwellen-Querdruck |σ_c,90| um >30% |
| **T45** | [`L46527`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46527) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | EC5 Gl. (6.15) Schub-Torsions-Interaktion, Gl. (B.10) Johansen-Dübel & Strandungspressung p_Strand |
| **T46** | [`L46539`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46539) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Kimmkanten-Rahmeneinspannung (L-Wurzelknie leiten Sohlenmoment in untere Bordwand ein) |
| **T47** | [`L46552`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46552) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Vierendeel-Rahmenbiegung & Eichen-Blockzargen-Entlastung an den 201 Schotttüren |
| **T48** | [`L46560`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46560) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | 2D-Zwischendeck-Durchlaufträgerbiegung σ_m = q·l²/(10·W) skaliert mit ICD-Knotenlast |
| **T49** | [`L46571`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46571) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Zohar-Ellen-Ausdehnung (300×50 E. vs. 260×21,5 E.) koppelt konsistent in Dachmasse & Vlasov-Torsion |
| **T50** | [`L46583`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46583) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Geschlossener Waben-Schott-Silo (I_y,Möhler > 400 m⁴, 0 Türen in S3/6/9/12 & 4:1 Schott-Widerstandsmoment) |
| **T51** | [`L46593`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46593) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | 720 Eichen-Wurzelknie (fixTag=5: Kimm-Wasserdruck nur außen, Norm-EC5 < 65% & Bruch-Stopp-Kopplung aktiv) |
| **T52** | [`L46602`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46602) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Hydrostatische Querquetschung (Querschott-Knicken), Dübel-Wechsellast-Verschleiß (K_ser) & Feuchte-Schüsselung (σ_cup,90) |
| **T53** | [`L46642`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46642) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Gen 8,1 Großer Gott-Wind (175 km/h Orkan, H=11,8m, 55° Schrägsee) — Innenschotten bruchsicher über 360° Phase |
| **T54** | [`L46687`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46687) | 5. 371-Tage-Chronik, Ermüdung & Instandhaltung | 371-Tage-Chronik (Kap. 14/15: Tag -20 leer -> Tag 20 Monsun -> Tag 146,5 Gott-Wind -> Tag 150 Grundsitz -> Tag 298 Ovoli -> Tag 371) |
| **T55** | [`L46692`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46692) | 5. 371-Tage-Chronik, Ermüdung & Instandhaltung | Palmgren-Miner-Wöhler-Akkumulation & logarithmische Madison-Dauerstandkurve k_mod(t) |
| **T56** | [`L46697`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46697) | 5. 371-Tage-Chronik, Ermüdung & Instandhaltung | Besatzungs-Wartung (Nachkeilen der 80.000 Hartholzdübel & Nachpechen in ruhiger Dünung) |
| **T57** | [`L46705`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46705) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Janssen-Silomechanik — Exakte Massenerhaltung (Wand + Sattel = 2.200 t) |
| **T58** | [`L46709`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46709) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Euler-Eytelwein-Seiltrieb (Paternoster F_Last > F_Leer, Ausnutzung < 100%) |
| **T59** | [`L46713`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46713) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | 3-Bahnen-Verteiler-Hub — Großtier-Rampen-Trittsicherheit S_Tritt > 1.50 |
| **T60** | [`L46717`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46717) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Alle 14 Einbauten-Systeme frei von NaN & im EC5-Bemessungsrahmen |
| **T61** | [`L46723`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46723) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | 9×8-Ellen-Seitentor Hydrostatik (F_w = ρ·g·A_w·h_c) & 6-Hände-Blockzargen-Schutz |
| **T62** | [`L46728`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46728) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Torricelli-Flutungs-Hydraulik Q_flood bei offenem 9×8-Ellen-Seitentor (4,0 Hände Bordwand) |
| **T63** | [`L46733`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46733) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Ortsaufgelöste Janssen-Silodruck-Erhöhung (Außenblöcke S3/S12 |Δx|=45m > Innen S6/S9 |Δx|=15m) |
| **T64** | [`L46737`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46737) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Vor-/Achterschiff-Asymmetrie der beiden Paternoster & Göpel (S4 @ X=35m vs. S11 @ X=105m) |
| **T65** | [`L46742`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46742) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Großtier-Rampen-Trittsicherheit S_Tritt(θ,φ) & 5,4-t-Basalt-Kombüsen (max g_eff S7/S13) |
| **T66** | [`L46752`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46752) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | 3D-Janssen-Tiefenprofil in den 224 Silowänden & 60°-Trichtersattel (Sattel > Fuß > Kopf) |
| **T67** | [`L46765`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46765) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Holz-Stein-Tribologie (6:1 Stockgetriebe im Ellen-Maß) & 12,3-kWh-Schichtfahrplan (5,5 h/Tag, Kap. 9.4–9.5) |
| **T68** | [`L46781`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46781) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | 3-Zweig-Kupplungsgetriebe (Exakte Drehmoment-Bilanz ΣM_Zweige = M_Göpel & Lastabwurf beim Auskuppeln) |
| **T69** | [`L46786`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46786) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Saint-Venant-Wellentorsion τ_t = 16·M_t/(π·D³) (Königswelle D=6H vs. 6:1-Querwellen D=2H) |
| **T70** | [`L46791`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46791) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Synchronisierte Deck-3-Einbauten (Basalt-Kombüse S7, Svalbard-Zeer S8 & Zimmermannswerkstatt |WERK|) |
| **T71** | [`L46799`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46799) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | 3D-Kraftfluss-Overlay (6 Zugkraft-Vektoren, 4 Drehmoment-Stromlinien & 3D-Schneckenwasserstrom) |
| **T72** | [`L46806`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46806) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Psychrometrie & Svalbard-Kühlung (T_FK <= T_Saatgut <= T_Stall) |
| **T73** | [`L46810`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46810) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Rinder-Physiologie (Boviner THI < 72 & DIN 18910 CO₂ < 3.000 ppm im Normfall) |
| **T74** | [`L46817`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46817) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | CIGR-Thermogenese (<8°C) vs. NRC-Anorexie-Drosselung (>26°C) |
| **T75** | [`L46823`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46823) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Ammoniak-Urease (NH₃ < 20 ppm) & Seewasser-Schwallspülung + CH₄-UEG |
| **T76** | [`L46827`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46827) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Vertikale 3-Decks-Temperaturschichtung (T_D1 < T_D2 < T_D3) |
| **T77** | [`L46832`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46832) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Bovine Kerntemperatur T_core (Hyperthermie bei Hitzestau) & Trinkwasserbedarf |
| **T78** | [`L46838`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46838) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | DIN-18910-Schadgas-Anstieg bei geschlossenen Schotttüren & Schwachlüftung |
| **T79** | [`L46844`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46844) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Sonnenbahn (Mittagszenit α = 90° - |φ - δ| = 68° vs. Mitternacht α < 0°) |
| **T80** | [`L46850`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46850) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Dalton-Gasgesetz & Magnus-Taupunkt (Feuchte Luft ist leichter als trockene Luft!) |
| **T81** | [`L46856`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46856) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Charnock-Meeresrauigkeit z_0 & logarithmisches Prandtl-Windprofil v_First > v_10 > v_Mid |
| **T82** | [`L46862`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46862) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Sol-Air-Dachbilanz — Solar-Aufheizung am Tag vs. Stefan-Boltzmann-Unterkühlung nachts |
| **T83** | [`L46867`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46867) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Psychrometrische Monsun-Dachkühlung (T_sol-air nähert sich bei Starkregen T_precip an) |
| **T84** | [`L46876`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46876) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Borda-Carnot-Schotttüren — Geschlossene Türen drosseln Lüftung & heizen Stall auf |
| **T85** | [`L46882`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46882) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | 14-Schritt-Bisektion & 2. Hauptsatz im Bilgen-Wärmetauscher (12°C vs. 34°C Meer) |
| **T86** | [`L46893`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46893) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Bâdgir-Innenschächte verhindern Dach-Kurzschluss & senken Turmfuß-Biegung um >60% |
| **T87** | [`L46906`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46906) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | 3D-Infrarot-Thermografie (T_Unterwasserwand < T_Innenstall < T_Sol-Air-Dach) |
| **T88** | [`L46915`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46915) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Bewegliche 3D-Sturmklappen an Zohar & Bâdgiren (Luv/Lee-Automatik im 1-Draw-Call InstancedMesh) |
| **T89** | [`L46922`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46922) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Dynamische Sturmklappen-Aerodynamik (α_Luv schließt im Orkan -> c_w sinkt & 94% Schlagregen-Abweisung) |
| **T90** | [`L46930`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46930) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | O2-Bilanz (RQ=0.85), H2S-Sulfat-Faulgas (Pumpen EIN vs. AUS), Erdregister & Silo-Taupunktschutz (> +3 K) |
| **T91** | [`L46946`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46946) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Manuelle Steuerung von Regentemperatur (T_Regen) & Bilgenwassertemperatur (T_Bilge) im Wärmenetzwerk |
| **T92** | [`L46971`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46971) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Wetter-Pakete A–D, 14 Szenario-Presets & 3D-Mikroklima-API (EC1-Schneelast, 3000m Ararat, ρ_See, Kombüse vs. Svalbard) |
| **T93** | [`L46983`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46983) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | Tierbestand (2.800 Gattungen | 6.350 Tiere | 1.100 t) & 3-m³-Svalbard-Tresor (40 Pithoi + 12 Zeer-Kühlröhren, Kap. 12.5) |
| **T94** | [`L47012`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47012) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | 3D-Fauna-Engine (6.350 Tiere, 8 Groß-Volieren vor Silos, Bâdgir-Öffnungen D1–D3 & Rinnen nur im Hauptgang) |
| **T95** | [`L47049`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47049) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | Zweisprachige DE/EN-Tooltip-Engine (100% Abdeckung für alle Dashboard-Keys, 67 GUI-Regler & 15 Szenarien) |
| **T96** | [`L47072`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47072) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | Modus-sensitiver 3D-Hover (Museum=Funktion | EC5=Kraft & % | Thermo=°C) & Auto-Gerätesprache (DE/EN) |
| **T97** | [`L47083`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47083) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | Numerische Stabilität — 0 NaN/Infinity-Werte im gesamten liveState |
| **T98** | [`L47144`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47144) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | 3D-Luftstrom-Netz (Arche.Groups.airflow3D ≥ 1500 Vertices), Zweikammer-Geschwindigkeitsfeld (Bâdgir Fall/Kamin, Atrium, Silo), CH4-Schichtung & Windwinkel-Kopplung (μ=90° > μ=0°) |
| **T99** | [`L47164`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47164) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | macOS Safari/Metal-GLSL-Konformität, Auto-FPS-Governor (≥ 30 FPS) & Mobile-UX |
| **T100** | [`L47246`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47246) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | Vollständige GPU-Beschleunigung (GPU-Stokes-Ozean, Ballistischer GPU-Splash-Shader & 0-ms-GPU-Instanz-Clipping) |
| **T101** | [`L47462`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47462) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | Bronzezeitlicher Werftplatz (Tag -7) & Ararat-Hochgebirgsmassiv (Tag 150–371) |

---
*Ende des generierten Index. Bei jeder Code-Modifikation `node index_arche.js` im Terminal ausführen!*
