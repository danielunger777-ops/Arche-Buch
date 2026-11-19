# ARCHE STRUKTUR-INDEX (`ARCHE_INDEX.md`)

> **Automatisch generiert durch `node index_arche.js`**  
> **Hauptdatei:** [`Arche Simulation 3.0.html`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html)  
> **Umfang:** **50.240 Zeilen** | **2959.8 KB**  
> **Stand:** 19.11.2026, 01:32:15

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
| [`L50237`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L50237) | `</script>` | Ende Haupt-JavaScript |
| [`L50238`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L50238) | `</body>` | Ende DOM-Hierarchie |

---

## 2. Arche Namespaces & Kern-Registries

| Zeile | Namespace | Beschreibung |
|:-----:|:----------|:-------------|
| [`L2015`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2015) | `window.Arche` | Arche Root-Namespace & State/Config/Kinematik-Arrays |
| [`L2187`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2187) | `Arche.UI` | UI-DOM-Bindings, Bilinguale Tooltips (DE/EN) & Viewport-Sync |
| [`L3089`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L3089) | `Arche.I18n` | Bilinguale Sprach-Engine (DE/EN), GUI-Labels & Option-Maps |
| [`L6754`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6754) | `Arche.Groups` | Three.js Szenengruppen-Registry (hullGroup, interiorGroup, shipyardGroup, etc.) |
| [`L8478`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8478) | `Arche.Materials` | Material-Registry (Gopherholz, Eiche, Zypresse, Bronze, Wasser, etc.) |
| [`L37558`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37558) | `Arche.Performance` | Auto-FPS-Governor (Tier 1-4 Quality-Manager) & Instanz-Reduktion |

---

## 3. Architektur-Meilensteine & Baugruppen-Banner

| Zeile | Abschnitt / Banner-Titel |
|:-----:|:-------------------------|
| [`L8515`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8515) | **BLENDER -> ARCHE .GLB-ASSET-PIPELINE (Arche.Assets)** |
| [`L17745`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17745) | **ANALYTISCHER 3D-KOLLISIONS-, FASS- & GANG-FREIHALTE-SOLVER (PBD, 14 ITER.)** |
| [`L19440`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19440) | **2. Z-Up-Geometrie-Helfer (Z ist OBEN!) & Ausrichtungs-Funktionen** |
| [`L19471`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19471) | **3. Höhenfunktionen & Geometrie-Helfer für Steppe und Hochgebirge** |
| [`L20390`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20390) | **PROZEDURALE BOTANIK: 4-QUADRANTEN-ATLAS & 3-STUFIGE VERÄSTELUNG (PAKET 1E)** |
| [`L22036`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22036) | **3B. Ultraleichter 12-km-Fernhorizont-Ring (~1.792 Tris, 0 % Weltkante)** |
| [`L22154`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22154) | **3C. 4-Band-Schatten-LOD-Helfer (Höhentextur-Bake + Projizierte GPU-Schatten)** |
| [`L22559`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22559) | **4. Kompletter Neuaufbau des Werftplatzes (Arche.Environment.buildShipyard3D)** |
| [`L24530`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24530) | **BAUGRUPPE 1: Baumfäll-Szene im Primärwald & Rollenträger-Knechte (Kap. 13.1)** |
| [`L24790`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24790) | **BAUGRUPPE 2: Göpel-Sägewerk, drehender Rotor, Kurbelschleife & Sägegruben (Kap. 13.1)** |
| [`L25098`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25098) | **BAUGRUPPE 3: 4 Holzkohlemeiler, Tubal-Kain-Schmiede & 9 Rauchsäulen (Kap. 13.1 & 13.2)** |
| [`L30862`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30862) | **4B. ASYNCHRONE BLENDER-BOTANIK-HYDRATION (6 ARTEN x 15 VARIANTEN x LOD0/LOD1)** |
| [`L32263`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32263) | **4C. ASYNCHRONE MESOPOTAMIA-CITY-KIT-HYDRATION & 4-STUFEN-LOD (0..3000 m)** |
| [`L32998`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32998) | **4D. ASYNCHRONE SHIPYARD-INDUSTRY-KIT-HYDRATION & 4-STUFEN-LOD (0..3000 m)** |
| [`L35568`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35568) | **3. Exakte Höhen-Synchronisation & Ausblenden des schwarzen seaGrid** |
| [`L39117`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39117) | **SYSTEM 1 (aPathType = 0.0): Vordere Frischluft-Schachtkammer & Erdregister |ZUL.|** |
| [`L39204`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39204) | **SYSTEM 2 (aPathType = 1.0 & 1.5): Stall-Durchstroemung & echte Tuer-Durchtritte** |
| [`L39246`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39246) | **SYSTEM 3 (aPathType = 2.0): Thermik, 1-Elle-Silospalt, Badgir-Lee-Kammer & Zohar** |
| [`L39419`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39419) | **SYSTEM 4 (aPathType = 3.0): Offenes 9x8-Ellen-Seitentor S7** |
| [`L46659`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46659) | **Screen-Space Contact Shadows (SSCS, Half-Res Depth, Desktop Tier 0/1, WebGL1)** |
| [`L48736`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48736) | **SUITE 1: 1. Ellen-Kanon, EN 338 & Clean Architecture (T01–T07)** |
| [`L48785`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48785) | **SUITE 2: 2. Hydrostatik, Massenbilanz & Schwimmstabilität (T08–T18)** |
| [`L48871`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48871) | **SUITE 3: 3. Wellenkinematik & 6-DOF-Hydrodynamik (T19–T30)** |
| [`L48950`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48950) | **SUITE 4: 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik (T31–T53)** |
| [`L49183`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49183) | **SUITE 5: 5. 371-Tage-Chronik, Ermüdung & Instandhaltung (T54–T56)** |
| [`L49225`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49225) | **SUITE 6: 6. Holz-Stein-Maschinenbau, Silos & Einbauten (T57–T71)** |
| [`L49327`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49327) | **SUITE 7: 7. Meteorologie, Bauphysik & Veterinär-Physiologie (T72–T92)** |
| [`L49503`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49503) | **SUITE 8: 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität (T93–T101)** |

---

## 4. 3D-Baugruppen

### 4.1 Werftplatz & Trockendock (`buildShipyard3D`)
> Bereich: **Zeile 22561 bis 33628** (Funktion `Arche.Environment.buildShipyard3D`)

| Zeile | Typ | Baugruppe / Eigenschaft | Details |
|:-----:|:---:|:------------------------|:--------|
| [`L22565`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22565) | `userData` | **shipyardGroup.userData.cribbingBlocks** | `[];` |
| [`L22566`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22566) | `userData` | **shipyardGroup.userData.pitchPits** | `[];` |
| [`L22578`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22578) | `userData` | **shipyardGroup.userData.heightMapTex** | `bakedSy.tex;` |
| [`L22581`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22581) | `Abschnitt` | **1. Topografisches Trockendock-Becken & Quellgebirge (1600 x 1600 m, 240 x 240 Segmente)** | `` |
| [`L22607`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22607) | `userData` | **shipyardGroup.userData.basinMesh** | `terrainMesh;` |
| [`L22640`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22640) | `userData` | **shipyardGroup.userData.horizonRingMesh** | `syHorizon.mesh;` |
| [`L22641`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22641) | `userData` | **shipyardGroup.userData.horizonMat** | `syHorizon.mat;` |
| [`L22727`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22727) | `userData` | **shipyardGroup.userData.waterAquaMat** | `waterAquaMat;` |
| [`L22754`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22754) | `userData` | **shipyardGroup.userData.basaltMasonryMat** | `basaltMat;` |
| [`L22796`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22796) | `userData` | **shipyardGroup.userData.aqueductFlowMat** | `aqueductFlowMat;` |
| [`L22815`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22815) | `userData` | **shipyardGroup.userData.canalBedMat** | `canalBedMat;` |
| [`L22855`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22855) | `userData` | **shipyardGroup.userData.canalWaterBedMat** | `canalWaterBedMat;` |
| [`L22996`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22996) | `userData` | **shipyardGroup.userData.riverWaterMat** | `riverWaterMat;` |
| [`L23019`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23019) | `userData` | **shipyardGroup.userData.flagstoneMat** | `flagstoneMat;` |
| [`L23037`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23037) | `userData` | **shipyardGroup.userData.lapisFriezeMat** | `lapisFriezeMat;` |
| [`L23050`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23050) | `userData` | **shipyardGroup.userData.ochreAwningMat** | `ochreAwningMat;` |
| [`L23101`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23101) | `userData` | **shipyardGroup.userData.shipyardKitPlacements** | `shipyardKitPlacements;` |
| [`L23102`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23102) | `userData` | **shipyardGroup.userData.shipyardKitDynamic** | `shipyardKitDynamic;` |
| [`L23103`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23103) | `userData` | **shipyardGroup.userData.procShipyardMeshes** | `procShipyardMeshes;` |
| [`L23152`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23152) | `Abschnitt` | **3. Die 60-Ellen-Beladerampe zum Seitentor (Backbord @ X = -5.0 m)** | `` |
| [`L23175`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23175) | `userData` | **shipyardGroup.userData.mainRampMesh** | `deckMesh;` |
| [`L23239`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23239) | `Abschnitt` | **3. Animierte Beladungs-Karawane vor der Flut (boardingGroup)** | `` |
| [`L23243`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23243) | `userData` | **shipyardGroup.userData.boardingGroup** | `boardingGroup;` |
| [`L23245`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23245) | `userData` | **shipyardGroup.userData.boardingWalkers** | `boardingWalkers;` |
| [`L23318`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23318) | `userData` | **shipyardGroup.userData.caravanMeta** | `caravanMeta;` |
| [`L23387`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23387) | `userData` | **shipyardGroup.userData.caravanInstMesh** | `caravanInstMesh;` |
| [`L23426`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23426) | `userData` | **shipyardGroup.userData.shipyardBirdsInstMesh** | `shipyardBirdsInstMesh;` |
| [`L23429`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23429) | `userData` | **shipyardGroup.userData.impactFX** | `Arche.Fauna.createGroundImpactFX(shipyardGroup, 64, 56, false);` |
| [`L23437`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23437) | `userData` | **shipyardGroup.userData.bunkeringGroup** | `bunkeringGroup;` |
| [`L23439`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23439) | `userData` | **shipyardGroup.userData.bunkeringWalkers** | `bunkeringWalkers;` |
| [`L23451`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23451) | `userData` | **shipyardGroup.userData.sackMat** | `sackMat;` |
| [`L23575`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23575) | `Abschnitt` | **4. Zugbrücken-Klappe (drawbridgeFlapGroup)** | `` |
| [`L23603`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23603) | `userData` | **shipyardGroup.userData.bronzeToolMat** | `bronzeToolMat;` |
| [`L23610`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23610) | `userData` | **shipyardGroup.userData.smithyMetalMat** | `smithyMetalMat;` |
| [`L23649`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23649) | `userData` | **shipyardGroup.userData.mudbrickMat** | `mudbrickMat;` |
| [`L23664`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23664) | `userData` | **shipyardGroup.userData.reedThatchMat** | `reedThatchMat;` |
| [`L23674`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23674) | `userData` | **shipyardGroup.userData.dryWorkers** | `[];` |
| [`L23717`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23717) | `userData` | **shipyardGroup.userData.scaffolds** | `[];` |
| [`L24053`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24053) | `userData` | **shipyardGroup.userData.craneWinchInstMeshes** | `_winchInstMeshes;` |
| [`L24054`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24054) | `userData` | **shipyardGroup.userData.craneOxInst** | `_craneOxInst;` |
| [`L24055`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24055) | `userData` | **shipyardGroup.userData.craneOxLocals** | `_craneOxLocals;` |
| [`L24066`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24066) | `userData` | **shipyardGroup.userData.craneHoistGroups** | `craneHoistGroups;` |
| [`L24067`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24067) | `userData` | **shipyardGroup.userData.craneWinchRotors** | `craneWinchRotors;` |
| [`L24069`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24069) | `Abschnitt` | **7. Kopher-Pechsiederei (3 Rundöfen mit glühendem Bad, Pechsiedern & Kalfater-Werkzeuglager)** | `` |
| [`L24264`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24264) | `userData` | **shipyardGroup.userData.smithyEmberMat** | `smithyEmberMat;` |
| [`L24276`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24276) | `userData` | **shipyardGroup.userData.terracottaMat** | `terracottaMat;` |
| [`L24397`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24397) | `userData` | **shipyardGroup.userData.hayMat** | `hayMat;` |
| [`L24432`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24432) | `Abschnitt` | **10. Kapitel 13: Holzriese & Rollenbahn** | `` |
| [`L24530`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24530) | `Kapitel 13 Baugruppe` | **BAUGRUPPE 1: Baumfäll-Szene im Primärwald & Rollenträger-Knechte (Kap. 13.1)** | `` |
| [`L24539`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24539) | `Abschnitt` | **1. Stehender 22-m-Zedernriese (D = 1.56 m) mit 3D-POM-Zedernborke, 4 Wurzelanläufen, einseitigem Kernholz-Fallkerb & 3-stufiger Krone** | `` |
| [`L24634`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24634) | `Abschnitt` | **3. Seilzug in der Krone + Umlenkrolle + 4 Zugochsen als 2 Doppelgespanne (Kettenlinie mit Durchhang)** | `` |
| [`L24684`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24684) | `Abschnitt` | **4. Nachbar-Baumstumpf (-139.2, -96.8) & waagerecht am Boden liegender 20-m-Zedernstamm ([-138.0, -96.0] bis [-122.0, -84.0]) mit 3D-POM-Zedernborke** | `` |
| [`L24786`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24786) | `userData` | **shipyardGroup.userData.fellingSceneGroup** | `fellingSceneGroup;` |
| [`L24790`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24790) | `Kapitel 13 Baugruppe` | **BAUGRUPPE 2: Göpel-Sägewerk, drehender Rotor, Kurbelschleife & Sägegruben (Kap. 13.1)** | `` |
| [`L24801`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24801) | `Abschnitt` | **1. Basalt-Bruchsteinring (R = 4.0 m) auf dem ebenen +2.80 m Plateau** | `` |
| [`L24809`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24809) | `Abschnitt` | **2. Feststehendes Eichen-Galgenportal & Basalt-Spurlager über dem Göpel** | `` |
| [`L24819`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24819) | `Abschnitt` | **3. Drehbare Untergruppe: sawmillCapstanRotor (Königswelle, Kammrad & Joche gebatcht + 4 gehörnte Zugochsen)** | `` |
| [`L24871`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24871) | `userData` | **shipyardGroup.userData.sawmillCapstanRotor** | `sawmillCapstanRotor;` |
| [`L24873`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24873) | `Abschnitt` | **4. Drehende Vorgelegewelle mit 8er-Stockritzel, Schwungrad & Kurbelzapfen (sawDriveShaftRotor)** | `` |
| [`L24880`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24880) | `userData` | **shipyardGroup.userData.sawdustMat** | `sawdustMat;` |
| [`L24920`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24920) | `userData` | **shipyardGroup.userData.sawDriveShaftRotor** | `sawDriveShaftRotor;` |
| [`L24922`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24922) | `Abschnitt` | **5. Lagerung der Vorgelegewelle: Oberer Längsträger über der Ochsenbahn (0 % Spur-Kollision!) + Außen-Lagerbock bei x = sx0 + 4.65** | `` |
| [`L24958`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24958) | `Abschnitt` | **6. Vertikales Sägegatter mit separat gelenkter Pleuelstange (Kurbelschleife)** | `` |
| [`L24975`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24975) | `userData` | **shipyardGroup.userData.sawFrame** | `sawFrameMesh;` |
| [`L24976`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24976) | `userData` | **shipyardGroup.userData.sawFrameBaseZ** | `sz0 + 1.2;` |
| [`L24988`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24988) | `userData` | **shipyardGroup.userData.sawPitmanGroup** | `sawPitmanGroup;` |
| [`L24989`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24989) | `userData` | **shipyardGroup.userData.sawPitmanBaseZ** | `sz0 + 1.82;` |
| [`L24990`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24990) | `userData` | **shipyardGroup.userData.sawPitmanCenterY** | `sy0;` |
| [`L24991`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24991) | `userData` | **shipyardGroup.userData.sawCrankCenterZ** | `sz0 + 2.62;` |
| [`L25094`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25094) | `userData` | **shipyardGroup.userData.sawPitGroup** | `sawPitGroup;` |
| [`L25098`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25098) | `Kapitel 13 Baugruppe` | **BAUGRUPPE 3: 4 Holzkohlemeiler, Tubal-Kain-Schmiede & 9 Rauchsäulen (Kap. 13.1 & 13.2)** | `` |
| [`L25114`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25114) | `userData` | **shipyardGroup.userData.meilerDomeMat** | `meilerDomeMat;` |
| [`L25124`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25124) | `userData` | **shipyardGroup.userData.meilerHotMat** | `meilerHotMat;` |
| [`L25177`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25177) | `userData` | **shipyardGroup.userData.smokeMat** | `smokeMat;` |
| [`L25204`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25204) | `userData` | **shipyardGroup.userData.smokePlumesGroup** | `smokePlumesGroup;` |
| [`L25205`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25205) | `userData` | **shipyardGroup.userData.smokePuffs** | `smokePuffs;` |
| [`L25221`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25221) | `userData` | **shipyardGroup.userData.smithyAnvilMat** | `smithyAnvilMat;` |
| [`L25320`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25320) | `userData` | **shipyardGroup.userData.smithyToolsGroup** | `smithyToolsGroup;` |
| [`L25323`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25323) | `Abschnitt` | **13. Kapitel 13: Frischwasser-Aquädukt & Raubtier-Rollkäfige** | `` |
| [`L25582`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25582) | `userData` | **shipyardGroup.userData.cityKitPlacements** | `cityKitPlacements;` |
| [`L25583`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25583) | `userData` | **shipyardGroup.userData.roadKitProps** | `roadKitProps;` |
| [`L25584`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25584) | `userData` | **shipyardGroup.userData.procCityMeshes** | `procCityMeshes;` |
| [`L26499`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26499) | `userData` | **shipyardGroup.userData.blenderOrnamentalSpecs** | `blenderOrnamentalSpots;` |
| [`L26822`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26822) | `userData` | **shipyardGroup.userData.organicRoadMesh** | `orgRoadMesh;` |
| [`L26823`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26823) | `userData` | **shipyardGroup.userData.organicRoadMat** | `orgRoadMat;` |
| [`L26841`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26841) | `userData` | **shipyardGroup.userData.roadMesh** | `roadMesh;` |
| [`L26842`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26842) | `userData` | **shipyardGroup.userData.roadMeshOrigMat** | `flagstoneMat;` |
| [`L27025`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27025) | `Abschnitt` | **1. Nord-Vorstadt (außerhalb Nord-Königstor bei y=+36..+52)** | `` |
| [`L27028`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27028) | `Abschnitt` | **2. Süd-Vorstadt (außerhalb Süd-Karawanentor bei y=-136..-162)** | `` |
| [`L27031`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27031) | `Abschnitt` | **3. Ostufer-Brückenkopf & Karawanserei (x=272..294, y=-68..-28)** | `` |
| [`L27495`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27495) | `userData` | **shipyardGroup.userData.cityBoats** | `cityBoats;` |
| [`L27546`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27546) | `userData` | **shipyardGroup.userData.cityWalkers** | `cityWalkers;` |
| [`L27801`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27801) | `Abschnitt` | **1. Ur-Schinar Süd & Südwest-Schwemmland (10 große Parzellen)** | `` |
| [`L27812`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27812) | `Abschnitt` | **2. Ur-Ostufer / Euphrat-Ostebene gegenüber der Metropole (10 weite Parzellen)** | `` |
| [`L27823`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27823) | `Abschnitt` | **3. Nisaba-Kornkammer / Südwest-Ebene (10 weite Parzellen)** | `` |
| [`L27834`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27834) | `Abschnitt` | **4. Eridu-Lagunengürtel / Südost-Ebene (8 große Parzellen)** | `` |
| [`L27843`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27843) | `Abschnitt` | **5. Girsu-Kanalauen / Ost-Ebene (8 weite Parzellen)** | `` |
| [`L27852`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27852) | `Abschnitt` | **6. Sippar & Nord-Euphrattal (6 große Parzellen)** | `` |
| [`L27859`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27859) | `Abschnitt` | **7. Larsam-Südoase / Süd-Weide & Getreidegürtel (6 weite Parzellen)** | `` |
| [`L28136`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28136) | `userData` | **shipyardGroup.userData.procCropInstMesh** | `cropInstMesh;` |
| [`L28137`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28137) | `userData` | **shipyardGroup.userData.blenderCropSpecs** | `{` |
| [`L28251`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28251) | `Abschnitt` | **1. Ur-Schinar Süd & SW (12)** | `` |
| [`L28258`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28258) | `Abschnitt` | **2. Ur-Ostufer gegenüber Metropole (12)** | `` |
| [`L28265`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28265) | `Abschnitt` | **3. Nisaba Kornkammer (12)** | `` |
| [`L28272`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28272) | `Abschnitt` | **4. Eridu Lagunengürtel (8)** | `` |
| [`L28277`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28277) | `Abschnitt` | **5. Girsu Ost-Ebene (8)** | `` |
| [`L28282`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28282) | `Abschnitt` | **6. Sippar & Nord-Euphrattal (6)** | `` |
| [`L28286`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28286) | `Abschnitt` | **7. Larsam Südoase (6)** | `` |
| [`L28403`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28403) | `userData` | **shipyardGroup.userData.farmInsts** | `{` |
| [`L28415`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28415) | `userData` | **shipyardGroup.userData.farmMovers** | `farmMovers;` |
| [`L28479`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28479) | `userData` | **shipyardGroup.userData.shadufInsts** | `shadufInsts;` |
| [`L28480`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28480) | `userData` | **shipyardGroup.userData.shadufBeams** | `shadufBeams;` |
| [`L28519`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28519) | `userData` | **shipyardGroup.userData.waterWheels** | `waterWheels;` |
| [`L28546`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28546) | `userData` | **shipyardGroup.userData.waterFoamMat** | `waterFoamMat;` |
| [`L28587`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28587) | `userData` | **shipyardGroup.userData.waterFoamInstMesh** | `waterFoamInstMesh;` |
| [`L28588`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28588) | `userData` | **shipyardGroup.userData.waterFoamNodes** | `foamNodes;` |
| [`L28589`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28589) | `userData` | **shipyardGroup.userData.waterFoamWakeStart** | `wakeSlotStart;` |
| [`L28604`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28604) | `userData` | **shipyardGroup.userData.cityBuildingShadowsInstMesh** | `bldgShadowInst;` |
| [`L28698`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28698) | `userData` | **shipyardGroup.userData.magurInstMeshes** | `boatParts.map(p => p.inst);` |
| [`L28699`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28699) | `userData` | **shipyardGroup.userData._magurAllCount** | `_magurAll.length;` |
| [`L28700`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28700) | `userData` | **shipyardGroup.userData._magurLogCount** | `_magurLogs.length;` |
| [`L28701`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28701) | `userData` | **shipyardGroup.userData._magurCargoCount** | `_magurCargo.length;` |
| [`L28702`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28702) | `userData` | **shipyardGroup.userData.updateMagurBoatMatrix** | `(bt, mat4) => {` |
| [`L28815`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28815) | `userData` | **shipyardGroup.userData.cityWalkerInstMeshes** | `cityWalkerInstMeshes;` |
| [`L28834`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28834) | `userData` | **shipyardGroup.userData.smokeInstMesh** | `smokeInst;` |
| [`L28942`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28942) | `userData` | **shipyardGroup.userData.boulderMat** | `boulderMat;` |
| [`L29000`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29000) | `userData` | **shipyardGroup.userData.boulderInstMesh** | `boulderInstMesh;` |
| [`L29022`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29022) | `userData` | **shipyardGroup.userData.logYardMat** | `logYardMat;` |
| [`L29062`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29062) | `userData` | **shipyardGroup.userData.logYardInstMesh** | `logYardInstMesh;` |
| [`L29247`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29247) | `userData` | **shipyardGroup.userData.steppeGrassInstMesh** | `steppeGrassInstMesh;` |
| [`L29248`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29248) | `userData` | **shipyardGroup.userData.blenderGrassSpecs** | `{ count: gPlaced, transforms: gPlaceTf, kind: gPlaceKind, colors:` |
| [`L29433`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29433) | `userData` | **shipyardGroup.userData.steppeShrubInstMesh** | `shrubInstMeshes[0];` |
| [`L29434`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29434) | `userData` | **shipyardGroup.userData.shrubInstMeshes** | `shrubInstMeshes;` |
| [`L29435`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29435) | `userData` | **shipyardGroup.userData.procShrubMeshes** | `shrubInstMeshes.slice();` |
| [`L29470`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29470) | `userData` | **shipyardGroup.userData.stumpBarkMat** | `stumpBarkMat;` |
| [`L29471`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29471) | `userData` | **shipyardGroup.userData.stumpCutMat** | `stumpCutMat;` |
| [`L29520`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29520) | `userData` | **shipyardGroup.userData.treeStumps** | `stumpsGroup;` |
| [`L30027`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30027) | `userData` | **shipyardGroup.userData.treesGroup** | `treesGroup;` |
| [`L30028`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30028) | `userData` | **shipyardGroup.userData.procTreeInstMeshes** | `allTreeInstMeshes.slice();` |
| [`L30029`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30029) | `userData` | **shipyardGroup.userData.blenderForestPlacements** | `{` |
| [`L30064`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30064) | `userData` | **shipyardGroup.userData.treeShadowInstMesh** | `_syTreeShadInst;` |
| [`L30067`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30067) | `userData` | **shipyardGroup.userData.forestTrunksInstMesh** | `forestTrunksInstMesh;` |
| [`L30068`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30068) | `userData` | **shipyardGroup.userData.allTreeInstMeshes** | `allTreeInstMeshes;` |
| [`L30338`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30338) | `Abschnitt` | **1. Bäume: Echtes 4-Stufen-LOD (Desktop: 150m / 500m / 1500m / 3000m, Werft & Ararat!)** | `` |
| [`L30601`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30601) | `Abschnitt` | **2. Prüfe die Strauch-Meshes (shrubInstMeshes — bis 640 m & hartes Frustum-Culling)** | `` |
| [`L30652`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30652) | `Abschnitt` | **3. Hydrierte Blender-Unterholz-, Gras-/Schilf-, Agrar- & Tempelzierbotanik-Gruppen (Werft & Ararat + Frustum-Culling)** | `` |
| [`L30812`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30812) | `Abschnitt` | **4. Frustum- & Distanz-Culling für Werft-Handwerker (dryWorkers) & Stadtbewohner-Zone (Ur-Schinar)** | `` |
| [`L31776`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31776) | `Abschnitt` | **1. Sträucher & Euphrat-Schilf/Papyrus aus procShrubMeshes** | `` |
| [`L31805`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31805) | `Abschnitt` | **2. Steppengras & Hochgras aus blenderGrassSpecs** | `` |
| [`L31828`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31828) | `Abschnitt` | **3. Mesopotamische Kulturpflanzen & Weinreben aus blenderCropSpecs** | `` |
| [`L31849`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31849) | `Abschnitt` | **4. Tempel-, Hofgarten-, Terrakotta-Kübel- & Lotus-Zierbotanik** | `` |
| [`L31936`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31936) | `Abschnitt` | **1. Ararat-Bäume nach (species, stage, varIdx) bündeln & auf 4-LOD-Pools (150/500/1500/3000m) mappen** | `` |
| [`L32094`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32094) | `Abschnitt` | **2. Ararat Sträucher, Schilf & Pioniergras als LOD-gepoolte ExtraGroups (mit uSproutGrowth & Frustum-Culling)** | `` |
| [`L33614`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33614) | `Abschnitt` | **5. Kompletter Neuaufbau des Ararat-Landeplatzes (Arche.Environment.buildAraratLandingSite3D)** | `` |

### 4.2 Ararat-Landeplatz (`buildAraratLandingSite3D`)
> Bereich: **Zeile 33629 bis 35662** (Funktion `Arche.Environment.buildAraratLandingSite3D`)

| Zeile | Typ | Baugruppe / Eigenschaft | Details |
|:-----:|:---:|:------------------------|:--------|
| [`L33633`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33633) | `userData` | **araratGroup.userData.isBuilt** | `true;` |
| [`L33634`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33634) | `userData` | **araratGroup.userData.saddleMesh** | `null;` |
| [`L33635`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33635) | `userData` | **araratGroup.userData.altarCoals** | `null;` |
| [`L33636`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33636) | `userData` | **araratGroup.userData.disembarkRampMesh** | `null;` |
| [`L33648`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33648) | `userData` | **araratGroup.userData.heightMapTex** | `bakedAra.tex;` |
| [`L33651`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33651) | `Abschnitt` | **1. Integriertes Hochgebirgs- & Sattel-Mesh (1.400 x 1.400 m, 208 x 208 Segmente mit zentrierter Auflösungs-Verdichtung für glatte Gipfelgrate & bündigen Kielsattel)** | `` |
| [`L33679`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33679) | `userData` | **araratGroup.userData.saddleMesh** | `terrainMesh;` |
| [`L33707`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33707) | `userData` | **araratGroup.userData.horizonRingMesh** | `araHorizon.mesh;` |
| [`L33708`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33708) | `userData` | **araratGroup.userData.horizonMat** | `araHorizon.mat;` |
| [`L33774`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33774) | `userData` | **araratGroup.userData.basaltCragsInstMesh** | `cragInst;` |
| [`L33896`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33896) | `userData` | **araratGroup.userData.waterfallGroup** | `waterfallGroup;` |
| [`L33897`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33897) | `userData` | **araratGroup.userData.waterfallUniforms** | `waterfallUniforms;` |
| [`L33899`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33899) | `Abschnitt` | **2. Fels-, Holz-, Feuer- & Bronzezeit-Materialien (alle WebGL1 AAA-gekoppelt & Thermo-/Struktur-fähig)** | `` |
| [`L33958`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33958) | `Abschnitt` | **3. Ausschiffungs-Steg & 4-stufiger Baufortschritt (rampStages) mit Catenary-Hanfseilen & Zimmermannsholz** | `` |
| [`L34210`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34210) | `userData` | **araratGroup.userData.rampStages** | `{` |
| [`L34216`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34216) | `userData` | **araratGroup.userData.disembarkRampMesh** | `gangwayDeck;` |
| [`L34222`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34222) | `Abschnitt` | **4. Großer Zyklopischer Dankopfer-Altar (Gen 8,20 / Ex 20,25), Opferfeuer (~600°C Thermo) & Noahs gesamte Familie (8 Personen)** | `` |
| [`L34293`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34293) | `userData` | **araratGroup.userData.altarStoneGroup** | `altarStoneGroup;` |
| [`L34307`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34307) | `userData` | **araratGroup.userData.altarCoals** | `coalMesh;` |
| [`L34331`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34331) | `userData` | **araratGroup.userData.uAltarFireThermo** | `uAltarFireThermo;` |
| [`L34332`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34332) | `userData` | **araratGroup.userData.uAltarFlicker** | `uAltarFlicker;` |
| [`L34358`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34358) | `userData` | **araratGroup.userData.altarEmberGlow** | `altarEmberGlow;` |
| [`L34365`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34365) | `userData` | **araratGroup.userData.altarFlickerLight** | `altarFlickerLight;` |
| [`L34367`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34367) | `Abschnitt` | **1. Volumetrisches fBm-Schwarzkörper-Opferfeuer (7 gekreuzte Flammen-Flächen = 1 Draw-Call, WebGL1-konform)** | `` |
| [`L34490`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34490) | `userData` | **araratGroup.userData.altarFlames** | `altarFlames;` |
| [`L34492`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34492) | `Abschnitt` | **2. Aufsteigende Funken & Glut-Asche (45 Funken in 1 THREE.Points Draw-Call, rein im Shader animiert)** | `` |
| [`L34557`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34557) | `userData` | **araratGroup.userData.altarSparks** | `altarSparks;` |
| [`L34559`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34559) | `Abschnitt` | **3. Weicher prozeduraler Opferrauch (Noise-Alpha-Billboards, keine harten Kugel-Silhouetten!)** | `` |
| [`L34638`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34638) | `userData` | **araratGroup.userData.altarSmokePuffs** | `altarSmokePuffs;` |
| [`L34671`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34671) | `userData` | **araratGroup.userData.altarGroup** | `altarGroup;` |
| [`L34674`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34674) | `Abschnitt` | **5. Kreativ-Highlight: Bronzezeitliches Basislager am Stegfuß (Terrakotta-Amphoren, Zedernkiste, Werkzeuge, Hanftau — mat zuerst!)** | `` |
| [`L34730`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34730) | `userData` | **araratGroup.userData.campGroup** | `campGroup;` |
| [`L34753`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34753) | `userData` | **araratGroup.userData.svalbardPlotGroup** | `svalbardPlotGroup;` |
| [`L34756`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34756) | `Abschnitt` | **6. Kreativ-Highlight: Schimmernde Gletscher-Schmelzwasser-Tümpel & Südtal-Tränkelagunen** | `` |
| [`L34789`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34789) | `userData` | **araratGroup.userData.meltwaterGroup** | `meltwaterGroup;` |
| [`L34828`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34828) | `userData` | **araratGroup.userData.strandedMatsGroup** | `strandedMatsGroup;` |
| [`L34829`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34829) | `userData` | **araratGroup.userData.matCentersAra** | `matCentersAra;` |
| [`L34832`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34832) | `Abschnitt` | **7. Weiträumige Auswanderungs-Korridore & Herden-Verteilung über das gesamte Ararat-Massiv (Kap. 14.5)** | `` |
| [`L34978`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34978) | `userData` | **araratGroup.userData.plateauQuadInstMesh** | `plateauQuadInstMesh;` |
| [`L34979`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34979) | `userData` | **araratGroup.userData.plateauMovers** | `plateauMovers;` |
| [`L34980`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34980) | `userData` | **araratGroup.userData.plateauFaunaGroup** | `plateauFaunaGroup;` |
| [`L34983`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34983) | `Abschnitt` | **8. Kreativ-Highlight: Taube mit Ölzweig (0), Rabe (1) + 42-Vögel-Schwarm aus Himmelsdeck / Zohar in freier Bergthermik (Kap. 14.5 Phase 1)** | `` |
| [`L35023`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35023) | `userData` | **araratGroup.userData.avianFlyInstMesh** | `avianFlyInstMesh;` |
| [`L35057`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35057) | `userData` | **araratGroup.userData.doveSprigGroup** | `doveSprigGroup;` |
| [`L35064`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35064) | `userData` | **araratGroup.userData.doveHeroAnchor** | `doveHeroAnchor;` |
| [`L35079`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35079) | `Abschnitt` | **9. Kreativ-Highlight: Regenbogen-Bundesbogen hoch & weit am Himmel HINTER dem Ararat-Massiv (Gen 9,13, 0% Bergschnitt!)** | `` |
| [`L35145`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35145) | `userData` | **araratGroup.userData.rainbowArcMesh** | `rainbowArcMesh;` |
| [`L35146`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35146) | `userData` | **araratGroup.userData.rainbowUniforms** | `rainbowUniforms;` |
| [`L35150`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35150) | `userData` | **araratGroup.userData.impactFX** | `Arche.Fauna.createGroundImpactFX(araratGroup, 64, 56, true);` |
| [`L35318`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35318) | `userData` | **araratGroup.userData.sproutGrassMesh** | `araratSproutGrassInstMesh;` |
| [`L35321`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35321) | `Abschnitt` | **11. Echte botanische Werft-Vegetation + Ovoli-Olivenstümpfe & Schilf auf Ararat (Kap. 15.3–15.6)** | `` |
| [`L35438`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35438) | `userData` | **araratGroup.userData.procAraTreeMeshes** | `_procAraTreeMeshes;` |
| [`L35439`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35439) | `userData` | **araratGroup.userData.blenderAraratHydrated** | `false;` |
| [`L35440`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35440) | `userData` | **araratGroup.userData.blenderAraratSpecs** | `[` |
| [`L35501`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35501) | `userData` | **araratGroup.userData.procAraAllMeshes** | `floraInstMeshes.slice();` |
| [`L35502`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35502) | `userData` | **araratGroup.userData.blenderAraratSpecs** | `araratGroup.userData.blenderAraratSpecs.concat(araShrubSpecs);` |
| [`L35525`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35525) | `userData` | **araratGroup.userData.ovoliShootsGroup** | `ovoliShootsGroup;` |
| [`L35556`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35556) | `userData` | **araratGroup.userData.treeShadowInstMesh** | `_araTreeShadInst;` |
| [`L35560`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35560) | `userData` | **araratGroup.userData.oliveSaplingsGroup** | `araratOliveSaplingsGroup;` |
| [`L35561`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35561) | `userData` | **araratGroup.userData.floraInstMeshes** | `floraInstMeshes;` |
| [`L35562`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35562) | `userData` | **araratGroup.userData.oliveSaplings** | `[];` |
| [`L35563`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35563) | `userData` | **araratGroup.userData.themedMats** | `themedMatsAra;` |
| [`L35568`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35568) | `Abschnitt` | **3. Exakte Höhen-Synchronisation & Ausblenden des schwarzen seaGrid** | `` |

---

## 5. Modul- & Top-Level-Funktionen

### 5.1 Arche.Procedural (Texturen, POM & Shader)

| Zeile | Funktion / Signatur |
|:-----:|:--------------------|
| [`L5221`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5221) | `Arche.Procedural.createInstantPlaceholderTex(r, g, b, repU = 1.0, repV = 1.0, isColor = true)` |
| [`L5402`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5402) | `Arche.Procedural.spawnMulticoreTexturePool()` |
| [`L5531`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5531) | `Arche.Procedural.buildWaterNormalTexture()` |
| [`L5576`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5576) | `Arche.Procedural.buildRoughnessTexture()` |
| [`L5627`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5627) | `Arche.Procedural.bindInteriorLightUniforms(shader)` |
| [`L5706`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5706) | `Arche.Procedural.attachCloseUpDetailLOD(mat, isPitchHull = false, isBarrelMat = false, isVolumetricBedding = false, isBasaltStone = false)` |
| [`L6094`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6094) | `Arche.Procedural.bindGpuShader(material, fixedMatId = 1)` |
| [`L6269`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6269) | `Arche.Procedural.bindEnvUniforms(shader)` |
| [`L6277`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6277) | `Arche.Procedural.injectEnvFogAndCloud(fragShader, worldPosExpr, applyCloudShadow = true, horizonShadowExpr = '')` |
| [`L6305`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6305) | `Arche.Procedural.bindMechPomShader(colorHex, mechType = 1)` |
| [`L6490`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6490) | `Arche.Procedural.cloneNoDeckClipMat(srcMat)` |
| [`L10154`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L10154) | `Arche.Procedural.buildBeddingAlphaShellTexture()` |
| [`L10239`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L10239) | `Arche.Procedural.buildVerticalHayFinTexture()` |
| [`L14309`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L14309) | `Arche.Procedural.updateInstancedBarrelsShader(ctx)` |
| [`L15208`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15208) | `Arche.Procedural.updateDrivetrainAndGalleyVisuals(ctx, fixRes, shiftState)` |
| [`L18661`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18661) | `Arche.Procedural.updateStormShutters3D(v_roof_kmh, mu_wind_rad, precip_mmh, ctx)` |
| [`L21831`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21831) | `Arche.Procedural.makeEnvMat(cacheKey, baseHex, rough, metal, fragExtraGLSL, options = {})` |
| [`L39065`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39065) | `Arche.Procedural.rebuildAirflow3DGeometry()` |
| [`L42589`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42589) | `Arche.Procedural.tempToHeatmapRGB(tempC)` |

### 5.2 Arche.Environment (Werft, Ararat & Botanik)

| Zeile | Funktion / Signatur |
|:-----:|:--------------------|
| [`L6852`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6852) | `Arche.Environment.loadTerrainTextures()` |
| [`L7006`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L7006) | `Arche.Environment._decodeUint16PngToFloat32(arrayBuf, zMin, zMax)` |
| [`L7079`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L7079) | `Arche.Environment.syncBlenderWorlds3D()` |
| [`L7142`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L7142) | `Arche.Environment.loadBlenderWorldMaps()` |
| [`L10444`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L10444) | `Arche.Environment.heightTexUniforms(()` |
| [`L18782`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18782) | `Arche.Environment.updateDeckSlicePlaneWorld()` |
| [`L19442`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19442) | `Arche.Environment.createZUpCylinderGeo(rTop, rBot, heightZ, segs = 12)` |
| [`L19449`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19449) | `Arche.Environment.addStrutBetweenPoints(parentGroup, p0, p1, rBot = 0.12, rTop = 0.12, mat = null, tooltipKey = null)` |
| [`L19506`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19506) | `Arche.Environment.evalRiverCenterX(y)` |
| [`L19512`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19512) | `Arche.Environment.evalRiverHalfWidth(y)` |
| [`L19517`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19517) | `Arche.Environment.evalRiverSurfaceZ(y)` |
| [`L19525`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19525) | `Arche.Environment.evalApproachRoadX(y)` |
| [`L19562`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19562) | `Arche.Environment.evalLakeLobeRadiusFrac(lake, x, y)` |
| [`L19572`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19572) | `Arche.Environment.evalLakeShorePoint(lake, ang, rFrac = 1.0)` |
| [`L19580`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19580) | `Arche.Environment.evalAlluvialLakeField(x, y)` |
| [`L19590`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19590) | `Arche.Environment.evalDistToPolyline(x, y, pts)` |
| [`L19604`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19604) | `Arche.Environment.evalCanalField(x, y)` |
| [`L19628`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19628) | `Arche.Environment._sampleBlenderHeightmapBilinear(hm, x, y)` |
| [`L19644`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19644) | `Arche.Environment.evalShipyardTerrainZ(x, y)` |
| [`L19794`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19794) | `Arche.Environment.evalAraratTerrainZ(x, y)` |
| [`L20393`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20393) | `Arche.Environment.getOrientalFoliageAtlasTex()` |
| [`L20607`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20607) | `Arche.Environment.pushLimb(buf, p0, p1, r0, r1, nSegs, rCol, gCol, bCol)` |
| [`L20665`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20665) | `Arche.Environment.pushFoliageCluster(buf, cx, cy, cz, rx, ry, rz, quadIdx, rCol, gCol, bCol, nCards = 9)` |
| [`L20724`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20724) | `Arche.Environment.pushPalmFrondRibbon(buf, spinePts, wStart, wMax, wEnd, rCol, gCol, bCol)` |
| [`L20786`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20786) | `Arche.Environment.createOrientalTreeGeo(speciesIdx, variantIdx)` |
| [`L21146`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21146) | `Arche.Environment.createOrientalShrubGeo(shrubType)` |
| [`L21240`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21240) | `Arche.Environment.getBotanyThicknessTex()` |
| [`L21271`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21271) | `Arche.Environment.applyOrientalFoliageShader(mat, options = {})` |
| [`L22038`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22038) | `Arche.Environment.createHorizonTerrainRing(opts)` |
| [`L22156`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22156) | `Arche.Environment.bakeTerrainHeightTex(evalLocalZFn, halfSpan = 3000.0, res = 256)` |
| [`L22192`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22192) | `Arche.Environment.getTreeShadowBlobTex()` |
| [`L22237`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22237) | `Arche.Environment.createProjectedTreeShadowsMesh(treesList, evalTerrainZFn, opts = {})` |
| [`L22387`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22387) | `Arche.Environment.createProjectedBuildingShadowsMesh(bldgBoxes, evalTerrainZFn, opts = {})` |
| [`L22509`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22509) | `Arche.Environment.evalShipyardHorizonZ(wx, wy, uRadOpt, isSkirtOpt)` |
| [`L22534`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22534) | `Arche.Environment.evalAraratHorizonZ(wx, wy, uRadOpt, isSkirtOpt)` |
| [`L22561`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22561) | `Arche.Environment.buildShipyard3D()` |
| [`L30118`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30118) | `Arche.Environment.updateVegetationLOD(cam, forceUpdate = false)` |
| [`L31205`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31205) | `Arche.Environment.registerBotanySpecies(speciesKey, opts = {})` |
| [`L31210`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31210) | `Arche.Environment.loadBotanyPlantPack(speciesKey, glbUrl, opts = {})` |
| [`L31224`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31224) | `Arche.Environment.applyBotanyShaderToObject(rootObj, opts = {})` |
| [`L31265`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31265) | `Arche.Environment.loadBlenderBotanyPacks()` |
| [`L31325`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31325) | `Arche.Environment._mergeShadowProxyGeo(parts)` |
| [`L31365`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31365) | `Arche.Environment._allocTreeShadowProxyPool(cap, archKey, refSp, packsMap, parentGrp, poolList, poolMap, meshAcc, tooltipKey, depthMat, namePrefix)` |
| [`L31403`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31403) | `Arche.Environment.hydrateBlenderForest3D(packsMap)` |
| [`L31639`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31639) | `Arche.Environment.hydrateBlenderExtraBotany3D(packsMap)` |
| [`L31877`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31877) | `Arche.Environment.hydrateBlenderAraratFlora3D(packsMap)` |
| [`L32244`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32244) | `Arche.Environment.hydrateBlenderBotany3D()` |
| [`L32435`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32435) | `Arche.Environment.hydrateMesopotamiaCityKit3D()` |
| [`L32845`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32845) | `Arche.Environment.updateCityLOD(cam, forceUpdate = false)` |
| [`L33158`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33158) | `Arche.Environment.hydrateShipyardIndustryKit3D()` |
| [`L33499`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33499) | `Arche.Environment.updateShipyardIndustryLOD(cam, forceUpdate = false)` |
| [`L33616`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33616) | `Arche.Environment.ensureAraratBuilt()` |
| [`L33629`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33629) | `Arche.Environment.buildAraratLandingSite3D()` |
| [`L35576`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35576) | `Arche.Environment.evalShipyardAbsTerrainZ(x, y)` |
| [`L35580`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35580) | `Arche.Environment.evalAraratAbsTerrainZ(x, y)` |
| [`L35585`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35585) | `Arche.Environment.evalTerrainBaseAbsNN(day)` |
| [`L35596`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35596) | `Arche.Environment.evalWaterLevelAbsNN(day)` |
| [`L35642`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35642) | `Arche.Environment.evalAbsoluteElevationCouple(wAbsNN, siteBaseNN, T_mean, hExtKeel)` |
| [`L35655`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35655) | `Arche.Environment.evalWaterRiseOffset(depth, T_mean, wAbsOverride, siteBaseOverride)` |
| [`L35663`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35663) | `Arche.Environment.updateLandmarksAndTerrain3D(depth, T_mean, dynHeaveZ, isThermalMode, isTexturedMode)` |
| [`L37476`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37476) | `Arche.Environment.updateFloatingMats3D(depth, waterRiseOffset, simTime, k, k_x, k_y, halfH, phi_rad, omega, wModel, mu_wind_rad, v_wind_ms, matsFrac, showWat)` |
| [`L46173`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46173) | `Arche.Environment.updateHullWaterFilm3D(depth, dt_sim, isThermalMode)` |

### 5.3 Arche.Fauna (Organische Tiere, Ochsen & Knechte)

| Zeile | Funktion / Signatur |
|:-----:|:--------------------|
| [`L15381`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15381) | `Arche.Fauna.subdivideCatmullPts(pts, subdiv = 2)` |
| [`L15405`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15405) | `Arche.Fauna.buildOrganicLoftGeometry(tubes, radSegs = 20, subdiv = 2)` |
| [`L15472`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15472) | `Arche.Fauna.buildPbrMaps()` |
| [`L15535`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15535) | `Arche.Fauna.getMorphTypeForGenusId(genusId)` |
| [`L15554`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15554) | `Arche.Fauna.getFaunaBoardingHeaderGLSL(isDepthPass = false)` |
| [`L15745`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15745) | `Arche.Fauna.getFaunaNormalDeformGLSL(archetypeMode = 'QUAD')` |
| [`L15812`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15812) | `Arche.Fauna.getFaunaVertexDeformGLSL(archetypeMode = 'QUAD', isDepthPass = false)` |
| [`L16314`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16314) | `Arche.Fauna.createFaunaDepthMaterial(archetypeMode = 'QUAD', locoScaleUniform = null)` |
| [`L16345`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16345) | `Arche.Fauna.createFaunaMaterial(rough = 0.62, baseHex = 0xffffff, coatClass = 'FUR', archetypeMode = 'QUAD')` |
| [`L16560`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16560) | `Arche.Fauna.createGroundImpactFX(parentGroup, maxPuffs = 64, maxRings = 56, isBasalt = false)` |
| [`L16722`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16722) | `Arche.Fauna.buildSculptedLimb(xHip, yHip, zHip, lenZ, rTop, rKnee, rHoof, cHide, isHind = false)` |
| [`L16736`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16736) | `Arche.Fauna.addHeadDetails(tubes, yEye, zEye, wHead, yEar, zEar, earW, earL, cIvory, hornType = 'BOVINE')` |
| [`L16788`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16788) | `Arche.Fauna.initArchetypesAndGoepelOxen()` |
| [`L17164`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17164) | `Arche.Fauna.getGenusInfo(genusId)` |
| [`L17199`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17199) | `Arche.Fauna.populateAllDecks()` |
| [`L17747`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17747) | `Arche.Fauna.resolveCollisionsAndClearCorridors()` |
| [`L18014`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18014) | `Arche.Fauna.syncVisibilityAndClip(zSliceMax)` |
| [`L18022`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18022) | `Arche.Fauna.updateShaderAndColors(ctx)` |
| [`L41557`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41557) | `Arche.Fauna.getIndividualHoverTooltip(ttKey, localPt, mode)` |

### 5.4 Arche.Physics (Wellen, Ozean, Mikroklima & Schichtpläne)

| Zeile | Funktion / Signatur |
|:-----:|:--------------------|
| [`L15044`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15044) | `Arche.Physics.evaluateGoepelShiftSchedule(timeOfDayHrs, isScheduleActive = false, overrideMode = null)` |
| [`L15076`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15076) | `Arche.Physics.evaluateArkTaxonomicCensus(payloadFrac = 1.0)` |
| [`L18591`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18591) | `Arche.Physics.evaluateShutterAerodynamics(headModeStr, v_roof_ms, rho_air, precip_mmh, isFullShipZohar = true, isBadgirActive = true, out = _shutterAeroScratch)` |
| [`L48327`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48327) | `Arche.Physics.evalWorldGroundSDF(wx, wy, wz)` |
| [`L48503`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48503) | `Arche.Physics.sampleMicroclimateAt(xShip, yShip, zShip, out = _microclimateScratch)` |
| [`L48589`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48589) | `Arche.Physics.evaluateAirflowVelocityField(xShip, yShip, zShip, out = _airflowVelScratch)` |

### 5.5 Arche.Performance & Quality-Governor

*Keine direkten Funktionsdeklarationen in dieser Sektion.*

### 5.6 Arche.UI & Bilinguale Tooltips

| Zeile | Funktion / Signatur |
|:-----:|:--------------------|
| [`L41689`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41689) | `Arche.UI.get3DHoverTooltipByMode(ttKey, localPt, overrideShaderMode = null)` |
| [`L42147`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42147) | `Arche.UI.getTooltip(key, lang = params.language, mode = Arche.State.viewShader, localPt = null)` |

### 5.7 Arche.Player & Kamera-Steuerung

| Zeile | Funktion / Signatur |
|:-----:|:--------------------|
| [`L48361`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48361) | `Arche.Player.flyTo(posArr, targetArr, durationSec = 1.25)` |
| [`L48376`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48376) | `Arche.Player.updateCameraAndLabels()` |

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
| [`L5208`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5208) | `cpuNoise2D(x, y)` |
| [`L5268`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5268) | `fastNoise2D(x, y)` |
| [`L5281`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5281) | `generateAlbedo(typeId)` |
| [`L5372`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5372) | `generateNormal(normId)` |
| [`L5446`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5446) | `applyFinishedJob(res)` |
| [`L5483`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5483) | `triggerMainThreadFallback()` |
| [`L5488`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5488) | `stepNextFallbackJob()` |
| [`L6499`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6499) | `orientCylinderUVsAlongAxis(geo, lengthM, radiusM)` |
| [`L6512`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6512) | `mergeTransformedGeos(entries)` |
| [`L6570`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6570) | `mergeRigidChildrenByMaterial(grp, excludeSet = null)` |
| [`L6622`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6622) | `createLanternPinionMesh(radius, length, nStaves, axis, diskMat, staveMat)` |
| [`L6651`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6651) | `createCrownWheelMesh(radius, rimThick, nTeeth, axis, toothSign, rimMat, toothMat)` |
| [`L6681`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6681) | `createArchimedeanHelixGeometry(rInner, rOuter, length, nTurns, radialSegs = 180)` |
| [`L6709`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6709) | `createWoodenDogClutchGroup(axis, hornbeamMat, oakMat)` |
| [`L8523`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8523) | `_computeTierAnisotropy(tierIdx)` |
| [`L8534`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8534) | `applyCleanTextureFiltering(tex, isColor)` |
| [`L8550`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8550) | `syncTextureAnisotropy(tierIdx)` |
| [`L8594`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8594) | `hasGLTFLoader()` |
| [`L8598`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8598) | `_getGLTFLoader(options)` |
| [`L8618`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8618) | `_isFileProtocol()` |
| [`L8622`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8622) | `_decodeBundleEntry(entry)` |
| [`L8642`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8642) | `_computeAssetModeColor(mat, viewShader, tEnv)` |
| [`L8658`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8658) | `attachArcheMaterialHooks(mat, options = {})` |
| [`L8881`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8881) | `syncViewShader(viewShader, tEnv)` |
| [`L8895`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8895) | `_parseGLTFBuffer(loader, arrayBuffer, resourcePath)` |
| [`L8910`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8910) | `_loadRawGLTFScene(slotKey, url, options = {})` |
| [`L8948`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8948) | `_applyTransformOpt(vec3Obj, val)` |
| [`L8955`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8955) | `_findManifestMeta(slotKey)` |
| [`L8970`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8970) | `loadGLBSlot(slotKey, url, targetParent, options = {})` |
| [`L9098`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9098) | `_isPlaceholderAlive(placeholder)` |
| [`L9108`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9108) | `_pruneStaleTargets(slotKey)` |
| [`L9122`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9122) | `_tryMountTarget(entry)` |
| [`L9207`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9207) | `registerReplaceTarget(slotKey, proceduralPlaceholderGroup, mountConfig = {})` |
| [`L9234`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9234) | `restoreProceduralFallback(slotKey)` |
| [`L9256`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9256) | `mountAllRegisteredSlots()` |
| [`L9269`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9269) | `initManifest(manifestUrl = 'assets/manifest.json')` |
| [`L9289`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9289) | `getStatus()` |
| [`L9308`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9308) | `extractInstancedTemplate(glbScene, options = {})` |
| [`L9367`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9367) | `createInstancedMesh(templateOrScene, maxCount, options = {})` |
| [`L9405`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9405) | `registerManagedMaterial(mat, options = {})` |
| [`L9428`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9428) | `configureSmoothLODGroup(lodGroup, opts = {})` |
| [`L11674`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11674) | `createLayerBucket()` |
| [`L11685`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11685) | `woodKeyToTexIdx(woodKey)` |
| [`L11692`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11692) | `resolvePartDynamicTexIdx(bucket, x, y, z, nx, ny, nz, elemType, matType, fixTag, forceTexIdx)` |
| [`L11736`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11736) | `addQuadToBucket(bucket, p1, p2, p3, p1_dup, p3_dup, p4, nx, ny, nz, elemType, matType, fixTag = 0,...)` |
| [`L11785`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11785) | `refreshAllWoodMaterialGroups()` |
| [`L11821`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11821) | `addBoxToBucket(bucket, x0, x1, y0, y1, z0, z1, elemType, matType, fixTag = 0, forceTexIdx = -1)` |
| [`L11829`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11829) | `addThickQuadToBucket(bucket, p1, p2, p3, p4, dx, dy, dz, nx, ny, nz, elemType, matType, fixTag = 0)` |
| [`L11846`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11846) | `addStormShutterInstance(xShip, yShip, zHinge, spanW, chordH, sideDir, isBadgirFlap = false)` |
| [`L11858`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11858) | `addHorizontalBarrelCylinderRow(bucket, wireArr, x0, x1, yCenter, zCenter, radius, nSegs, fixTag = 3)` |
| [`L11864`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11864) | `addBoneTimberInstance(x0, y0, z0, x1, y1, z1, radius)` |
| [`L11874`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11874) | `addVolumetricBeddingZone(x0, x1, y0, y1, zBase, thicknessZ, moundPeakZ = 0.0, densityWeight = 1.0)` |
| [`L11883`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11883) | `buildVolumetricHullWallsAndDecks()` |
| [`L11907`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11907) | `addDeckBayWithCutout(x0, x1, y0, y1, z0, z1, cX0, cX1, cY0, cY1, matType, addGuardrail = false, openXSi...)` |
| [`L12514`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12514) | `addWireBox(x0, x1, y0, y1, z0, z1)` |
| [`L12752`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12752) | `addBarrelPerpendicularToWallY(bucket, wireArr, xCenter, y0, y1, zCenter, radius, nSegs, fixTag = 3, cutawayHide ...)` |
| [`L12769`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12769) | `addTransverseBulkheadBarrelRack(xR0, xR1, yRack0, yRack1, zKantTop, zDeck, rowCountsZ, forceColsY = 0)` |
| [`L12799`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12799) | `addChineWallBarrelRack(xCh0, xCh1, yCh0, yCh1, zDeck, isPortSide, nColsX = 5, nRowsY = 2)` |
| [`L12859`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12859) | `addDeck1MegafaunaStallRow(xM0, xM1, yBack, yFront, nStalls)` |
| [`L12943`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12943) | `addFlushChuteSlottedOakGrating3D(xG0, xG1, yC0, yC1, zDeck)` |
| [`L12957`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12957) | `addOpenFlushChute3D(x0, x1, y0, y1, zDeck)` |
| [`L13166`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L13166) | `addDeck2AnimalPenRow(xP0, xP1, yBack, yFront, nPens)` |
| [`L13374`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L13374) | `addDeck3AviaryBlock(xA0, xA1, y0, y1, nCages)` |
| [`L13459`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L13459) | `addDeck3RodentHoneycombBlock(xR0, xR1, yShelf, nCols, halfDepthY = 0.38)` |
| [`L14012`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L14012) | `buildGeometryMaterialGroups(geo, metaList)` |
| [`L14216`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L14216) | `pushBedShellQuad(p1, p2, p3, p4, u0, v0, u1, v1, hLay0, hLay1 = hLay0)` |
| [`L14425`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L14425) | `createGoepelWheelGroup(xCenter)` |
| [`L14909`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L14909) | `createAnimatedPaternosterGroup(xCenter)` |
| [`L15028`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15028) | `updatePaternosterAnimation(pGroup, liftPhase)` |
| [`L15089`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15089) | `setDogClutchVisualState(clutchGrp, engaged)` |
| [`L15101`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15101) | `updateGoepelTransmissionKinematics(gMaster, deltaAngleRad, shiftState = null)` |
| [`L18142`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18142) | `writeSiloConeCell(cellIdx, x0, x1, y0, y1, zE00, zE10, zE11, zE01, xM, yM, zApex, rA, gA, bA, rE, gE...)` |
| [`L18167`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18167) | `writeTkWatQuad(qIdx, p1x, p1y, p1z, p2x, p2y, p2z, p3x, p3y, p3z, p4x, p4y, p4z, nx, ny, nz, rT, ...)` |
| [`L18195`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18195) | `updateSiloGrainAndHighTanks3D(H_silo_fill_m, d3TankFillFrac, d2SpuelFillFrac, rollRad, pitchRad, isThermalMode, ...)` |
| [`L18285`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18285) | `buildSloshingTankVolume(x0, x1, y0, y1, zBot, zMeanWat, rTop, gTop, bTop, rBot, gBot, bBot, phaseOff)` |
| [`L18400`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18400) | `writeBilgeQuad(qIdx, p1x, p1y, p1z, p2x, p2y, p2z, p3x, p3y, p3z, p4x, p4y, p4z, nx, ny, nz, rT, ...)` |
| [`L18420`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18420) | `getDoubleBottomChamberType(iSec, jBay)` |
| [`L18431`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18431) | `updateBilgeWater3D(h_bilge_eff, rollRad, pitchRad, isThermalMode, T_bilge_C, T_sea_C)` |
| [`L18539`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18539) | `pushShutterBox(x0, x1, y0, y1, z0, z1, uScale = 1.0, vScale = 1.0)` |
| [`L18797`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18797) | `updateLayerVisibilities()` |
| [`L18979`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18979) | `writeVolRestQuad(posArr, colArr, quadIdx, xA, yA, xB, yB, rTop, gTop, bTop, rBot, gBot, bBot)` |
| [`L19240`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19240) | `spawnSplashParticle(wx, wy, wz, vx, vy, vz, pSize = 1.6, lifeDur = 1.0, jitterXY = 1.6)` |
| [`L19404`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19404) | `updateGate3D(mode)` |
| [`L19936`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19936) | `createGrassTuftGeo(h = 0.40, nBlades = 5, wBase = 0.12, wTop = 0.035)` |
| [`L19965`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19965) | `createShrubClusterGeo()` |
| [`L20009`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20009) | `createStaticGeometryBatcher()` |
| [`L20012`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20012) | `getBuffers(mat)` |
| [`L20021`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20021) | `addBox(mat, cx, cy, cz, sx, sy, sz, rx = 0, ry = 0, rz = 0)` |
| [`L20028`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20028) | `rotXform(x, y, z)` |
| [`L20038`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20038) | `rotNorm(nx, ny, nz)` |
| [`L20070`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20070) | `addStrut(mat, p0, p1, rTop, rBot, nSegs = 6)` |
| [`L20119`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20119) | `addCatenaryRope(mat, p0, p1, radius = 0.02, sagM = 0.14, nSteps = 12, nRadSegs = 6, windAmp = 0.035)` |
| [`L20216`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20216) | `addTentClothPanel(mat, cx, cy, cz, widthX, slopeL, rotX, nSegX = 12, nSegY = 6, rotZ = 0.0)` |
| [`L20224`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20224) | `evalPt(u, v)` |
| [`L20245`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20245) | `addGeometry(mat, srcGeo, matrix = null)` |
| [`L20273`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20273) | `buildMeshes(parentGroup, tooltipKey = null, opts = {})` |
| [`L20300`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20300) | `buildChunkedMeshes(parentGroup, tooltipKey = null, opts = {})` |
| [`L20706`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20706) | `calcNorm(px, py, pz)` |
| [`L22650`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22650) | `makeShipyardEnvMat(cacheKey, baseHex, rough, metal, fragExtraGLSL, options = {})` |
| [`L23321`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23321) | `nextRandC()` |
| [`L24076`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24076) | `nextRandVar()` |
| [`L25333`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25333) | `addAquaWater(geo, px, py, pz, rx = 0, quat = null)` |
| [`L25635`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25635) | `rotXY(cx, cy, lx, ly, yaw)` |
| [`L25639`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25639) | `addVillageSmoke(ox, oy, oz, pIdx)` |
| [`L25644`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25644) | `addMudbrickHouse(cx, cy, w, d, hWall, yaw, hasAwning, hasLadder, idx)` |
| [`L26054`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26054) | `addUrCourtyardHouse(cx, cy, w, d, h1, h2, yaw, awMat, hasOven, idx, targetBatch = cityBatch)` |
| [`L26088`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26088) | `addWingRoof(wx, wy, ww, wd, wh, addVigas)` |
| [`L26172`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26172) | `addUrInsula(cx, cy, totW, totD, cols, rows, yaw, seedOff, targetBatch = cityBatch)` |
| [`L26194`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26194) | `addUrCityGate(gx, gy, outYaw)` |
| [`L26262`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26262) | `addWallSpan(x0, y0, x1, y1, hWall, thick, hasCrenels = true, useKitWall = false)` |
| [`L26526`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26526) | `pushRoadTri(ax, ay, az, au, av, bx, by, bz, bu, bv, cx, cy, cz, cu, cv)` |
| [`L26530`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26530) | `addFlagstoneRoad(pts, width, tier = 0)` |
| [`L26607`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26607) | `pushStonePlazaPad(cxP, cyP, wP, dP, nxP = 4, nyP = 4, zLift = 0.042)` |
| [`L26645`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26645) | `pushOrgRoadTri(ax, ay, az, au, av, af, bx, by, bz, bu, bv, bf, cx, cy, cz, cu, cv, cf)` |
| [`L26650`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26650) | `addOrganicRoad(pts, width, meanderAmp = 0.55)` |
| [`L27041`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27041) | `appendCarvedCanalRibbon(pts, halfW, startExt = 0.0, endExt = 0.0, zStart = zCanalW, zEnd = zCanalW, watPts...)` |
| [`L27042`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27042) | `buildDensePath(srcPts)` |
| [`L27311`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27311) | `addRiverIntakeSluice(ix, iy, dirToLandX, zWat, spanHalf = 3.3)` |
| [`L27445`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27445) | `addMagurBoatSlot(hasLogs, x, y, z, yawZ, boatInfo)` |
| [`L27559`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27559) | `addCanalArchBridge(bx, by, yaw, spanW = 10.6, roadW = 4.2)` |
| [`L27576`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27576) | `addTimberJetty(jx, jy, yaw, len = 10.5, zWater = 0.80)` |
| [`L27594`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27594) | `addGrainSilo(sx, sy, rad = 2.35, h = 4.4)` |
| [`L27603`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27603) | `addMudhifHut(mx, my, yaw, len = 7.2, wid = 3.8)` |
| [`L27622`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27622) | `addTownKiln(kx, ky, smokeIdx)` |
| [`L27764`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27764) | `evalRegionalRoadDist(px, py)` |
| [`L27776`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27776) | `isSafeAgriSpot(wx, wy, minRoadDist = 5.0)` |
| [`L27868`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27868) | `addUprightStrawRick(fx, fy, fIdx, withThreshFloor)` |
| [`L27904`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27904) | `addFieldShelter(sx, sy, yaw)` |
| [`L28018`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28018) | `nextRandCrop()` |
| [`L28418`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28418) | `addCanalWeir(wx, wy, yaw, spanW = 6.4, zWater = 0.82)` |
| [`L28844`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28844) | `isInUrCityOrSuburb(x, y, pad = 0.0)` |
| [`L28852`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28852) | `isShipyardWorkZone(x, y, pad = 0.0, forTrees = false)` |
| [`L29200`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29200) | `nextRandG()` |
| [`L29270`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29270) | `nextRandS()` |
| [`L29485`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29485) | `nextRandSt()` |
| [`L29601`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29601) | `nextRandT()` |
| [`L30884`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30884) | `_loadSharedBotanyTextures()` |
| [`L30976`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30976) | `_prepTexForBotany(tex, isColor, repeatWrap)` |
| [`L30992`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30992) | `_adaptBotanyMaterial(species, srcMat, isFol, sharedTex, opts = {})` |
| [`L31062`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31062) | `_extractSpeciesPack(species, glbScene, sharedTex, opts = {})` |
| [`L32275`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32275) | `_createCityTrimMaterial(srcMat, isRoad = false)` |
| [`L32411`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32411) | `_openCityGateDoorsGeometry(geo)` |
| [`L33010`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33010) | `_createShipyardTrimMaterial(srcMat, isHot = false)` |
| [`L35263`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35263) | `nextRandSp()` |
| [`L35339`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35339) | `nextRandSap()` |
| [`L37679`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37679) | `getDeviceClass()` |
| [`L37691`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37691) | `detectInitialTier()` |
| [`L37723`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37723) | `resolveTierFromMode(pMode)` |
| [`L37733`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37733) | `applyTier(tierIdx, force = false)` |
| [`L37800`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37800) | `resetGovernorClock()` |
| [`L37808`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37808) | `tickGovernor(nowMs)` |
| [`L37865`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37865) | `getCurrentSpec()` |
| [`L37869`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37869) | `setProfileMode(modeStr)` |
| [`L37880`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37880) | `init()` |
| [`L37888`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37888) | `restoreStandardVisibilities()` |
| [`L37928`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37928) | `updateExteriorPortalCulling(cam)` |
| [`L38077`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38077) | `updateLegendMode(mode)` |
| [`L38208`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38208) | `updateScenarioDescription(scenName)` |
| [`L38517`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38517) | `translateGUI(lang)` |
| [`L38548`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38548) | `translateDOM(lang)` |
| [`L38770`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38770) | `showExpeditionBriefing()` |
| [`L38777`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38777) | `hideExpeditionBriefing()` |
| [`L38784`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38784) | `selectAppModeAndStart(mode)` |
| [`L38817`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38817) | `toggleLabExpeditionMode()` |
| [`L38826`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38826) | `reopenOnboardingModal(directBriefing = false)` |
| [`L38833`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38833) | `toggleLanguage(forceLang)` |
| [`L39041`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39041) | `getBadgirPairStationsX(count)` |
| [`L39049`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39049) | `updateBucketMeshGeometry(bucket)` |
| [`L39083`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39083) | `addPath(fn, pathType)` |
| [`L39105`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39105) | `bezier3(p0, p1, p2, p3, u)` |
| [`L39442`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39442) | `updateZoharAndBadgirGeometry()` |
| [`L39691`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39691) | `computeBadgirMassTons()` |
| [`L39724`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39724) | `resetWaveAndShipState()` |
| [`L39980`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39980) | `triggerPauseEquilibriumRelax()` |
| [`L39984`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39984) | `markCustomPreset()` |
| [`L40041`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40041) | `syncQuickViewDock()` |
| [`L40057`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40057) | `toggleQuickAirflow()` |
| [`L40063`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40063) | `setQuickShader(modeStr)` |
| [`L40069`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40069) | `setQuickSlice(sliceStr)` |
| [`L40075`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40075) | `setQuickWall(wallStr)` |
| [`L40109`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40109) | `enterArkInterior()` |
| [`L40126`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40126) | `flyToInteriorDeck(deckKey)` |
| [`L40153`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40153) | `updateInteriorNavHUD(forceNow = false)` |
| [`L40371`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40371) | `toggleHighlightTour()` |
| [`L40376`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40376) | `toggleFreeCameraMode(forceVal)` |
| [`L40556`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40556) | `applyPiersonMoskowitzWindSea(v_kmh)` |
| [`L40629`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40629) | `evaluateExpeditionLogistics(day, rain_mmh = 0.0, T_stall_C = 20.8, depth_m = 0.0, woodMoisturePct = 13.5, out ...)` |
| [`L40756`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L40756) | `evaluateBiblicalChronicleState(day, instantSnap = false)` |
| [`L41157`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41157) | `syncChronicleUI()` |
| [`L41242`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41242) | `toggleChronicleVoyage()` |
| [`L41260`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41260) | `startPreFloodBunkering()` |
| [`L41275`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41275) | `resetVoyageToLand()` |
| [`L41289`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41289) | `changeChronicleSpeed(val)` |
| [`L41294`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41294) | `scrubChronicleDay(val)` |
| [`L41337`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41337) | `computeRawICDNodeKN(wallIdx, lvlIdx, stIdx)` |
| [`L41383`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41383) | `computeScaledICDNodeKN(wallIdx, lvlIdx, stIdx, precomputedRawSum = null)` |
| [`L41399`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41399) | `generateICDMarkdownReport()` |
| [`L41477`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41477) | `translateMarkdownReportEN(md)` |
| [`L41497`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41497) | `openICDModal()` |
| [`L41510`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41510) | `refreshICDMarkdown()` |
| [`L41518`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41518) | `closeICDModal()` |
| [`L41521`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41521) | `copyICDMarkdown()` |
| [`L41531`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41531) | `downloadICDMarkdown()` |
| [`L41544`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41544) | `getFixturePopularTooltip(key)` |
| [`L42159`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42159) | `renderActiveTooltipContent()` |
| [`L42176`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42176) | `showDynamicTooltip(source, key, clientX, clientY)` |
| [`L42186`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42186) | `positionSciTooltip(clientX, clientY)` |
| [`L42200`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42200) | `hideSciTooltip()` |
| [`L42232`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42232) | `resolve3DFixtureTooltipKey(hitObj, localPt, instanceId = undefined)` |
| [`L42371`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42371) | `_collectHoverTargets(node, out)` |
| [`L42390`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42390) | `perform3DRaycastInspect(clientX, clientY)` |
| [`L42522`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42522) | `computeUtilizationRGB(etaEC5, etaBruch, blinkState, outRGB)` |
| [`L42565`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42565) | `computeThermalRGB(tempC, outRGB)` |
| [`L42594`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42594) | `getBeaufortInfo(v_kmh)` |
| [`L42609`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42609) | `update3DLabel(mesh, domElem)` |
| [`L42622`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42622) | `getBarColor(etaEC5, etaBruch)` |
| [`L42629`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42629) | `computeHullSectionProperties(hasCrossBracing, hasHeavyPlanking, hasSwelling, tempInteriorC, effWaveHalfLen_m)` |
| [`L42784`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42784) | `evalWebES(z_upper)` |
| [`L42833`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42833) | `evalESRatio(z_val)` |
| [`L42894`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42894) | `evaluateOceanWave(x_ship, y_ship, k, k_x, k_y, halfH, phi_rad, omega, depth, waveModel, out)` |
| [`L42949`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42949) | `getStationEffectiveKNPerMeter(stIdx)` |
| [`L42970`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42970) | `evaluateICDWeightPerMeterMN(xs, totalWeightMN, payloadFrac)` |
| [`L42980`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42980) | `writeVolumeQuad(posArr, colArr, quadIdx, xA, yA, zTopA, rA, gA, bA, xB, yB, zTopB, rB, gB, bB, zFl...)` |
| [`L42995`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42995) | `writeFilmQuad(posArr, normArr, colArr, quadIdx, x0, y0, zBot0, zTop0, x1, y1, zBot1, zTop1, nx, ...)` |
| [`L43015`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43015) | `initOceanWaveWorker()` |
| [`L43021`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43021) | `evaluateExactHydrostatics(M_akt_t, V_ext_keels_m3, h_ext_keel_m, out = _maritimeScratch, rho_sea_override = ...)` |
| [`L43040`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43040) | `evaluateTransverseWaveFKFactor(k_y, B = B_SHIP)` |
| [`L43047`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43047) | `evaluateStripAddedMassAndSlam(subDraft, depth, geomSubDraft, draftBB_clean, draftSB_clean, vUpMid, vUpBB, vUpSB,...)` |
| [`L43078`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43078) | `stepSemiImplicitHeavePitch(heaveZ, heaveVel, heaveAcc, M11, C11, K11, pitchRad, pitchVel, pitchAcc, M22, C22,...)` |
| [`L43104`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43104) | `evaluateMetabolicHeatResponse(T_stall_C)` |
| [`L43114`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43114) | `evaluateBarnPhysiologyAndGasBalance(T_mean_C, RH_pct, T_bilge_C, Q_solar_roof_kW, Q_bio_total_kW, steamRate_kgh, V_dot...)` |
| [`L43221`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43221) | `evaluateAstronomyAndPsychrometrics(timeOfDay, latitude, cloudCover, extHumidity, precipIntensity, tAir, tWater, airPr...)` |
| [`L43336`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43336) | `evaluateCharnockWindAndSolAir(v_wind_10_kmh, H_wave, T_mean, badgirHeight, mu_wind_rad, rho_air, M_akt_t, GM_tra...)` |
| [`L43428`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43428) | `evaluateMassAndStabilityBalance(payloadPct, precipIntensity, dynRollRad, oxenBioEff, timeOfDay, out = _massStabScr...)` |
| [`L43611`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43611) | `evaluateThermalNetworkAndVentilation(T_current_C, prevRelHumidity, P_goepel_W, payloadFrac, waterDepth_m, T_mean, freeb...)` |
| [`L43731`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43731) | `evalStallHeatBalanceResidual(T_cand)` |
| [`L43973`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43973) | `evaluateDAlembertStripDynamics(k, k_x, k_y, halfH, phi_rad, omega, depth, wModel, mu_rad, T_mean, KG_height, M_ak...)` |
| [`L44260`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44260) | `evaluateRollAndSurgeSwayDynamics(dynamicMotion, autoPlay, dt_phys, halfH, depth, T_mean, BM_radius, KG_height, GM_t...)` |
| [`L44458`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44458) | `evaluateSideGateHydrostatics(gateMode, isSideGateOpen, zWaterAtGate, T_mean, dynHeaveZ, dynPitchRad, dynRollRad...)` |
| [`L44584`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44584) | `evaluateInternalFixturesMechanics(payloadFrac, oxenPresence, oxenBioEfficiency, H_wave, dynRollRad, dynPitchRad, dyn...)` |
| [`L44599`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44599) | `evalLocalG(x_m, y_m)` |
| [`L45079`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45079) | `evaluateHullHotspotsAndLUTs(payloadFrac, M_nutz_akt, m_roof_dyn, M_rain_roof_t, M_rain_soak_t, h_bilge_eff_m, ...)` |
| [`L45371`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45371) | `evaluateFatigueAndHotspotEC5(fatigueEnabled, chronicleActive, autoPlay, dt_phys, eqHoursStep, H_wave, omega, ma...)` |
| [`L45518`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45518) | `evaluate3DFieldPointMechanicsAndThermal(meta, isBadgirPart, isRoofPart, ctx = _shaderFrameCtx, out = _fieldPointScratch)` |
| [`L45985`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45985) | `evaluateVertexBufferColors(metaList, targetColArr, isBadgirPart, isRoofPart = false, ctx = _shaderFrameCtx)` |
| [`L46086`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46086) | `evaluateEC5AndNorris(sigma_glob, sigma_loc_bend, sigma_90_trans, tau_xy, matObj, isScarfLoc, d_member_m...)` |
| [`L46679`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46679) | `_initSSCS()` |
| [`L46825`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46825) | `_resizeSSCS()` |
| [`L46837`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46837) | `_isSSCSNearScene()` |
| [`L46857`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46857) | `_runSSCSContactPass()` |
| [`L46964`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46964) | `_compositeSSCSContactPass()` |
| [`L46974`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46974) | `animate(isSingleTestStep = false)` |
| [`L48431`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48431) | `syncMobileViewportAndPerf(isInit = false)` |
| [`L48693`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48693) | `runArcheUnitTests()` |
| [`L48702`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48702) | `assertTest(suite, name, condition, detailStr)` |
| [`L50016`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L50016) | `openUnitTestModal(e)` |
| [`L50145`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L50145) | `prewarmSimulationShaders()` |
| [`L50177`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L50177) | `startArcheSimulationCleanly()` |


---

## 6. Vollständiges Unit-Test-Kataster (T01 bis T101)

> Ausgeführt durch `runArcheUnitTests()` (ab Zeile ~27436).  
> **Gesamt: 101 Tests** — 100% abgedeckt.

| ID | Zeile | Test-Suite | Test-Bezeichnung |
|:--:|:-----:|:-----------|:-----------------|
| **T01** | [`L48738`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48738) | 1. Ellen-Kanon, EN 338 & Clean Architecture | Biblische Hauptabmessungen (300 × 50 × 30 Ellen) |
| **T02** | [`L48743`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48743) | 1. Ellen-Kanon, EN 338 & Clean Architecture | 6–5–4–3-Handbreiten-Normquerschnitte (Glatte Handbreiten ohne cm-Rundung) |
| **T03** | [`L48748`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48748) | 1. Ellen-Kanon, EN 338 & Clean Architecture | EN 338 Fraktilmodul E_0,05 (Laubholz 0.84 vs. Nadelholz 0.67) |
| **T04** | [`L48754`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48754) | 1. Ellen-Kanon, EN 338 & Clean Architecture | EC5 Bemessungswerte f_d = f_k * k_mod / γ_M (NKL 3) |
| **T05** | [`L48758`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48758) | 1. Ellen-Kanon, EN 338 & Clean Architecture | 300-Knoten-ICD-Kataster Vollständigkeit & Symmetrie |
| **T06** | [`L48768`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48768) | 1. Ellen-Kanon, EN 338 & Clean Architecture | Glatte Ellen- & Handbreiten-Konsistenz (0,000 mm Zentimeter-Rundungsabweichung) |
| **T07** | [`L48779`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48779) | 1. Ellen-Kanon, EN 338 & Clean Architecture | Clean-Architecture-Registry (Arche.Groups & Arche.Materials), Basalt-Kombüse S7, Svalbard-Zeer & 0-ms-Schnittebene |
| **T08** | [`L48789`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48789) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Archimedisches Gleichgewicht T = (V_disp - V_Kiele) / (L*B*C_B) |
| **T09** | [`L48796`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48796) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Volumetrische Sensitivität V × ρ_EN338 (Sohle 5,0 Hände -> 6,5 Hände) |
| **T10** | [`L48800`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48800) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Metazentrische Anfangsstabilität GM_eff > 4.0 m |
| **T11** | [`L48804`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48804) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Freie-Oberflächen-Unterdrückung durch 7.500 Einzelfässer |
| **T12** | [`L48808`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48808) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | 3 Äußere Eichenkiele (Strandungs-Aufstandsfläche ≥ 350 m²) |
| **T13** | [`L48814`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48814) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Exakter Steiner-Formschwerpunkt KB & BM inkl. 3 Außenkiele |
| **T14** | [`L48826`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48826) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | D1-Fass-Wechselballast senkt KG, erhöht Tiefgang T & aufrichtendes Moment M·GM |
| **T15** | [`L48833`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48833) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Manning-Strickler-Regenwasseraufstau & Bilgenzulauf bei 1.200 mm/h Monsun |
| **T16** | [`L48839`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48839) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Kreiszylinder-Sehnenbreite b(h) = 2·√(R²-(h-R)²) maximiert |ΔGM| bei 50% Füllung |
| **T17** | [`L48845`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48845) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Flacher Bilgensumpf Pocket-Effekt dämpft freie Oberfläche bei starker Krängung |
| **T18** | [`L48866`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48866) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | 3D-Fass-Inventur (7.920 echte 8-Hände-Fässer) & 0 % Kollision (Silos, Schotttüren S1/14, Bâdgir-Schächte & Schnecken S4/11) |
| **T19** | [`L48875`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48875) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Miche-Flachwasser-Brecherlimit (H=20m bei d=12m begrenzt) |
| **T20** | [`L48882`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48882) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Stokes 3. Ordnung Kamm-Aufsteilung (η_Stokes > η_Sinus bei θ=0) |
| **T21** | [`L48888`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48888) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Wendel/Kim-Flachwasser-Quetschströmung (m'_add,flach > m'_add,tief) |
| **T22** | [`L48894`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48894) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Wagner/Ochi-Motter Keilslamming (Deadrise-Dämpfung bei φ=10° Krängung) |
| **T23** | [`L48900`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48900) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Analytischer Quer-Beugungsfaktor κ_trans(k_y*B) in Lang- vs. Kurzwelle |
| **T24** | [`L48906`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48906) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Unbedingte Stabilität des semi-impliziten Winkler-Felskontakt-Integrators |
| **T25** | [`L48913`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48913) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Nichtlineare Wall-Sided-Stabilität GZ(φ) > GM·sin(φ) bei φ = 15° |
| **T26** | [`L48924`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48924) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Ikeda-Kimmwirbeldämpfung B44_ikeda (Mittelkiel Y=0 + 2 Kimmkiele Y=±17.5 E.) |
| **T27** | [`L48928`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48928) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Vollständiger 6-DOF Roll-Trägheitstensor I_xx,tot (Struktur + ICD-Ladung + Added Mass) |
| **T28** | [`L48936`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48936) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | 2D-Beugungs-Surge (Auslöschung sinc(k_x·L/2) = 0 bei λ = L = 140 m vs. Langwelle) |
| **T29** | [`L48941`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48941) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Bodenkontakt-Arretierung (groundLock = 0 sperrt Surge/Sway bei Strandung) |
| **T30** | [`L48945`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48945) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Exakte Einzelpositionen (15 Längsgurte, 45 Stützen & 8 Bâdgire @ Y=±4.18m) in I_xx |
| **T31** | [`L48956`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48956) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Exakter Querkraft-Abschluss V_z(0) = 0 & V_z(140m) = 0 MN |
| **T32** | [`L48960`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48960) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Exakter Biegemoment-Abschluss M_y(0) = 0 & M_y(140m) = 0 MNm |
| **T33** | [`L48964`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48964) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Elastische 2-Knoten-Whipping-Eigenfrequenz f_1 im Zielband |
| **T34** | [`L48970`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48970) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | EC5 Anhang B (Möhler) — Wurzelknie erhöhen γ_mean & I_y,eff |
| **T35** | [`L48978`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48978) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | EC5 Gl. (6.17) — Exakt 100.0% bei σ_t,0,d = η_Schäft * f_t,0,d |
| **T36** | [`L48987`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48987) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | EC5 Gl. (6.19) — Quadratische Druck-Biege-Interaktion (u_c² + u_m) |
| **T37** | [`L48993`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48993) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | EC5 Gl. (6.23) — Biegeknicken (λ_rel > 0.30 -> k_c < 1.0 erhöht Ausnutzung) |
| **T38** | [`L48999`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48999) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | EC5 Gl. (3.1) — Höhenbeiwert k_h = (150/h)^0.2 für h < 150 mm |
| **T39** | [`L49005`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49005) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | 2D-Norris — Biaxiale Zug-Querdruck-Verschärfung (-u_0*u_90 > 0) |
| **T40** | [`L49009`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49009) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Johansen-Dübeltragfähigkeit (EC5 Gl. 8.6 & B.10) & Gustafsson k_v |
| **T41** | [`L49016`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49016) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Headless 2×2-D'Alembert-Löser schließt V_z(L), M_y(L) & M_t(L) exakt auf Null |
| **T42** | [`L49024`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49024) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | 3-Kiele-Winkler-Bodenkontakt erzeugt aufrichtendes Rollmoment (Y = ±17.5 E.) |
| **T43** | [`L49033`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49033) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Biaxiale Schrägbiegung (M_z), Vlasov-Wölbkrafttorsion & Racking-Schub in der 15×4-Hotspot-Suche |
| **T44** | [`L49044`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49044) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | 300-Knoten-Querdruck-LUT — 45 Eichen-Königsstützen senken Schwellen-Querdruck |σ_c,90| um >30% |
| **T45** | [`L49050`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49050) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | EC5 Gl. (6.15) Schub-Torsions-Interaktion, Gl. (B.10) Johansen-Dübel & Strandungspressung p_Strand |
| **T46** | [`L49062`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49062) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Kimmkanten-Rahmeneinspannung (L-Wurzelknie leiten Sohlenmoment in untere Bordwand ein) |
| **T47** | [`L49075`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49075) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Vierendeel-Rahmenbiegung & Eichen-Blockzargen-Entlastung an den 201 Schotttüren |
| **T48** | [`L49083`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49083) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | 2D-Zwischendeck-Durchlaufträgerbiegung σ_m = q·l²/(10·W) skaliert mit ICD-Knotenlast |
| **T49** | [`L49094`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49094) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Zohar-Ellen-Ausdehnung (300×50 E. vs. 260×21,5 E.) koppelt konsistent in Dachmasse & Vlasov-Torsion |
| **T50** | [`L49106`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49106) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Geschlossener Waben-Schott-Silo (I_y,Möhler > 400 m⁴, 0 Türen in S3/6/9/12 & 4:1 Schott-Widerstandsmoment) |
| **T51** | [`L49116`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49116) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | 720 Eichen-Wurzelknie (fixTag=5: Kimm-Wasserdruck nur außen, Norm-EC5 < 65% & Bruch-Stopp-Kopplung aktiv) |
| **T52** | [`L49125`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49125) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Hydrostatische Querquetschung (Querschott-Knicken), Dübel-Wechsellast-Verschleiß (K_ser) & Feuchte-Schüsselung (σ_cup,90) |
| **T53** | [`L49165`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49165) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Gen 8,1 Großer Gott-Wind (175 km/h Orkan, H=11,8m, 55° Schrägsee) — Innenschotten bruchsicher über 360° Phase |
| **T54** | [`L49210`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49210) | 5. 371-Tage-Chronik, Ermüdung & Instandhaltung | 371-Tage-Chronik (Kap. 14/15: Tag -20 leer -> Tag 20 Monsun -> Tag 146,5 Gott-Wind -> Tag 150 Grundsitz -> Tag 298 Ovoli -> Tag 371) |
| **T55** | [`L49215`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49215) | 5. 371-Tage-Chronik, Ermüdung & Instandhaltung | Palmgren-Miner-Wöhler-Akkumulation & logarithmische Madison-Dauerstandkurve k_mod(t) |
| **T56** | [`L49220`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49220) | 5. 371-Tage-Chronik, Ermüdung & Instandhaltung | Besatzungs-Wartung (Nachkeilen der 80.000 Hartholzdübel & Nachpechen in ruhiger Dünung) |
| **T57** | [`L49228`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49228) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Janssen-Silomechanik — Exakte Massenerhaltung (Wand + Sattel = 2.200 t) |
| **T58** | [`L49232`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49232) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Euler-Eytelwein-Seiltrieb (Paternoster F_Last > F_Leer, Ausnutzung < 100%) |
| **T59** | [`L49236`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49236) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | 3-Bahnen-Verteiler-Hub — Großtier-Rampen-Trittsicherheit S_Tritt > 1.50 |
| **T60** | [`L49240`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49240) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Alle 14 Einbauten-Systeme frei von NaN & im EC5-Bemessungsrahmen |
| **T61** | [`L49246`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49246) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | 9×8-Ellen-Seitentor Hydrostatik (F_w = ρ·g·A_w·h_c) & 6-Hände-Blockzargen-Schutz |
| **T62** | [`L49251`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49251) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Torricelli-Flutungs-Hydraulik Q_flood bei offenem 9×8-Ellen-Seitentor (4,0 Hände Bordwand) |
| **T63** | [`L49256`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49256) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Ortsaufgelöste Janssen-Silodruck-Erhöhung (Außenblöcke S3/S12 |Δx|=45m > Innen S6/S9 |Δx|=15m) |
| **T64** | [`L49260`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49260) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Vor-/Achterschiff-Asymmetrie der beiden Paternoster & Göpel (S4 @ X=35m vs. S11 @ X=105m) |
| **T65** | [`L49265`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49265) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Großtier-Rampen-Trittsicherheit S_Tritt(θ,φ) & 5,4-t-Basalt-Kombüsen (max g_eff S7/S13) |
| **T66** | [`L49275`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49275) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | 3D-Janssen-Tiefenprofil in den 224 Silowänden & 60°-Trichtersattel (Sattel > Fuß > Kopf) |
| **T67** | [`L49288`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49288) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Holz-Stein-Tribologie (6:1 Stockgetriebe im Ellen-Maß) & 12,3-kWh-Schichtfahrplan (5,5 h/Tag, Kap. 9.4–9.5) |
| **T68** | [`L49304`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49304) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | 3-Zweig-Kupplungsgetriebe (Exakte Drehmoment-Bilanz ΣM_Zweige = M_Göpel & Lastabwurf beim Auskuppeln) |
| **T69** | [`L49309`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49309) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Saint-Venant-Wellentorsion τ_t = 16·M_t/(π·D³) (Königswelle D=6H vs. 6:1-Querwellen D=2H) |
| **T70** | [`L49314`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49314) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Synchronisierte Deck-3-Einbauten (Basalt-Kombüse S7, Svalbard-Zeer S8 & Zimmermannswerkstatt |WERK|) |
| **T71** | [`L49322`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49322) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | 3D-Kraftfluss-Overlay (6 Zugkraft-Vektoren, 4 Drehmoment-Stromlinien & 3D-Schneckenwasserstrom) |
| **T72** | [`L49329`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49329) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Psychrometrie & Svalbard-Kühlung (T_FK <= T_Saatgut <= T_Stall) |
| **T73** | [`L49333`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49333) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Rinder-Physiologie (Boviner THI < 72 & DIN 18910 CO₂ < 3.000 ppm im Normfall) |
| **T74** | [`L49340`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49340) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | CIGR-Thermogenese (<8°C) vs. NRC-Anorexie-Drosselung (>26°C) |
| **T75** | [`L49346`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49346) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Ammoniak-Urease (NH₃ < 20 ppm) & Seewasser-Schwallspülung + CH₄-UEG |
| **T76** | [`L49350`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49350) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Vertikale 3-Decks-Temperaturschichtung (T_D1 < T_D2 < T_D3) |
| **T77** | [`L49355`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49355) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Bovine Kerntemperatur T_core (Hyperthermie bei Hitzestau) & Trinkwasserbedarf |
| **T78** | [`L49361`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49361) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | DIN-18910-Schadgas-Anstieg bei geschlossenen Schotttüren & Schwachlüftung |
| **T79** | [`L49367`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49367) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Sonnenbahn (Mittagszenit α = 90° - |φ - δ| = 68° vs. Mitternacht α < 0°) |
| **T80** | [`L49373`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49373) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Dalton-Gasgesetz & Magnus-Taupunkt (Feuchte Luft ist leichter als trockene Luft!) |
| **T81** | [`L49379`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49379) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Charnock-Meeresrauigkeit z_0 & logarithmisches Prandtl-Windprofil v_First > v_10 > v_Mid |
| **T82** | [`L49385`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49385) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Sol-Air-Dachbilanz — Solar-Aufheizung am Tag vs. Stefan-Boltzmann-Unterkühlung nachts |
| **T83** | [`L49390`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49390) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Psychrometrische Monsun-Dachkühlung (T_sol-air nähert sich bei Starkregen T_precip an) |
| **T84** | [`L49399`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49399) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Borda-Carnot-Schotttüren — Geschlossene Türen drosseln Lüftung & heizen Stall auf |
| **T85** | [`L49405`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49405) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | 14-Schritt-Bisektion & 2. Hauptsatz im Bilgen-Wärmetauscher (12°C vs. 34°C Meer) |
| **T86** | [`L49416`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49416) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Bâdgir-Innenschächte verhindern Dach-Kurzschluss & senken Turmfuß-Biegung um >60% |
| **T87** | [`L49429`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49429) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | 3D-Infrarot-Thermografie (T_Unterwasserwand < T_Innenstall < T_Sol-Air-Dach) |
| **T88** | [`L49438`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49438) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Bewegliche 3D-Sturmklappen an Zohar & Bâdgiren (Luv/Lee-Automatik im 1-Draw-Call InstancedMesh) |
| **T89** | [`L49445`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49445) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Dynamische Sturmklappen-Aerodynamik (α_Luv schließt im Orkan -> c_w sinkt & 94% Schlagregen-Abweisung) |
| **T90** | [`L49453`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49453) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | O2-Bilanz (RQ=0.85), H2S-Sulfat-Faulgas (Pumpen EIN vs. AUS), Erdregister & Silo-Taupunktschutz (> +3 K) |
| **T91** | [`L49469`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49469) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Manuelle Steuerung von Regentemperatur (T_Regen) & Bilgenwassertemperatur (T_Bilge) im Wärmenetzwerk |
| **T92** | [`L49494`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49494) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Wetter-Pakete A–D, 14 Szenario-Presets & 3D-Mikroklima-API (EC1-Schneelast, 3000m Ararat, ρ_See, Kombüse vs. Svalbard) |
| **T93** | [`L49506`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49506) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | Tierbestand (2.800 Gattungen | 6.350 Tiere | 1.100 t) & 3-m³-Svalbard-Tresor (40 Pithoi + 12 Zeer-Kühlröhren, Kap. 12.5) |
| **T94** | [`L49535`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49535) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | 3D-Fauna-Engine (6.350 Tiere, 8 Groß-Volieren vor Silos, Bâdgir-Öffnungen D1–D3 & Rinnen nur im Hauptgang) |
| **T95** | [`L49572`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49572) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | Zweisprachige DE/EN-Tooltip-Engine (100% Abdeckung für alle Dashboard-Keys, 67 GUI-Regler & 15 Szenarien) |
| **T96** | [`L49595`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49595) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | Modus-sensitiver 3D-Hover (Museum=Funktion | EC5=Kraft & % | Thermo=°C) & Auto-Gerätesprache (DE/EN) |
| **T97** | [`L49606`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49606) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | Numerische Stabilität — 0 NaN/Infinity-Werte im gesamten liveState |
| **T98** | [`L49667`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49667) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | 3D-Luftstrom-Netz (Arche.Groups.airflow3D ≥ 1500 Vertices), Zweikammer-Geschwindigkeitsfeld (Bâdgir Fall/Kamin, Atrium, Silo), CH4-Schichtung & Windwinkel-Kopplung (μ=90° > μ=0°) |
| **T99** | [`L49687`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49687) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | macOS Safari/Metal-GLSL-Konformität, Auto-FPS-Governor (≥ 30 FPS) & Mobile-UX |
| **T100** | [`L49769`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49769) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | Vollständige GPU-Beschleunigung (GPU-Stokes-Ozean, Ballistischer GPU-Splash-Shader & 0-ms-GPU-Instanz-Clipping) |
| **T101** | [`L49985`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49985) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | Bronzezeitlicher Werftplatz (Tag -7) & Ararat-Hochgebirgsmassiv (Tag 150–371) |

---
*Ende des generierten Index. Bei jeder Code-Modifikation `node index_arche.js` im Terminal ausführen!*
