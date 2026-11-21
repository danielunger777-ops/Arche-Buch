# ARCHE STRUKTUR-INDEX (`ARCHE_INDEX.md`)

> **Automatisch generiert durch `node index_arche.js`**  
> **Hauptdatei:** [`Arche Simulation 3.0.html`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html)  
> **Umfang:** **54.789 Zeilen** | **3191.5 KB**  
> **Stand:** 21.11.2026, 15:16:16

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
| [`L1509`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L1509) | `</style>` | Ende CSS-Stylesheets |
| [`L1512`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L1512) | `<body...>` | DOM-Hierarchie, HUD-Container & Canvas |
| [`L2049`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2049) | `<script>` | Beginn Haupt-JavaScript (Three.js & Arche Engine) |
| [`L54786`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L54786) | `</script>` | Ende Haupt-JavaScript |
| [`L54787`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L54787) | `</body>` | Ende DOM-Hierarchie |

---

## 2. Arche Namespaces & Kern-Registries

| Zeile | Namespace | Beschreibung |
|:-----:|:----------|:-------------|
| [`L2052`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2052) | `window.Arche` | Arche Root-Namespace & State/Config/Kinematik-Arrays |
| [`L2224`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2224) | `Arche.UI` | UI-DOM-Bindings, Bilinguale Tooltips (DE/EN) & Viewport-Sync |
| [`L3127`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L3127) | `Arche.I18n` | Bilinguale Sprach-Engine (DE/EN), GUI-Labels & Option-Maps |
| [`L6954`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6954) | `Arche.Groups` | Three.js Szenengruppen-Registry (hullGroup, interiorGroup, shipyardGroup, etc.) |
| [`L8744`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8744) | `Arche.Materials` | Material-Registry (Gopherholz, Eiche, Zypresse, Bronze, Wasser, etc.) |
| [`L41115`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41115) | `Arche.Performance` | Auto-FPS-Governor (Tier 1-4 Quality-Manager) & Instanz-Reduktion |

---

## 3. Architektur-Meilensteine & Baugruppen-Banner

| Zeile | Abschnitt / Banner-Titel |
|:-----:|:-------------------------|
| [`L8781`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8781) | **BLENDER -> ARCHE .GLB-ASSET-PIPELINE (Arche.Assets)** |
| [`L18385`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18385) | **ANALYTISCHER 3D-KOLLISIONS-, FASS- & GANG-FREIHALTE-SOLVER (PBD, 14 ITER.)** |
| [`L20141`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20141) | **1B. ARCHE-WELLE A: BLENDER-GRUNDSTRUKTUR + 6 ZIMMERMANNS-HERO-MODULE** |
| [`L20902`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20902) | **1C. ARCHE-WELLE B: MASCHINENBAU (B1), 7.920 FÄSSER, HABITATE (B2) & MANNSCHAFTSRÄUME (B3)** |
| [`L21440`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21440) | **A) WELLE B1 — MASCHINENBAU (S4 & S11), 7.920 FÄSSER, SPEZIALRÄUME & OPTIK** |
| [`L21698`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21698) | **B) WELLE B2 — TIER-LEBENSWELTEN D1–D3, 1K-HEUBALLEN & 5 PIKTOGRAMME** |
| [`L21871`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21871) | **C) WELLE B3 — MANNSCHAFTSRÄUME FÜR NOAHS 8-KÖPFIGE FAMILIE (S7 DECK 3)** |
| [`L21951`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21951) | **2. Z-Up-Geometrie-Helfer (Z ist OBEN!) & Ausrichtungs-Funktionen** |
| [`L21982`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21982) | **3. Höhenfunktionen & Geometrie-Helfer für Steppe und Hochgebirge** |
| [`L22901`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22901) | **PROZEDURALE BOTANIK: 4-QUADRANTEN-ATLAS & 3-STUFIGE VERÄSTELUNG (PAKET 1E)** |
| [`L24593`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24593) | **3B. Ultraleichter 12-km-Fernhorizont-Ring (~1.792 Tris, 0 % Weltkante)** |
| [`L24711`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24711) | **3C. 4-Band-Schatten-LOD-Helfer (Höhentextur-Bake + Projizierte GPU-Schatten)** |
| [`L25116`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25116) | **4. Kompletter Neuaufbau des Werftplatzes (Arche.Environment.buildShipyard3D)** |
| [`L27109`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27109) | **BAUGRUPPE 1: Baumfäll-Szene im Primärwald & Rollenträger-Knechte (Kap. 13.1)** |
| [`L27365`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27365) | **BAUGRUPPE 2: Göpel-Sägewerk, drehender Rotor, Kurbelschleife & Sägegruben (Kap. 13.1)** |
| [`L27673`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27673) | **BAUGRUPPE 3: 4 Holzkohlemeiler, Tubal-Kain-Schmiede & 9 Rauchsäulen (Kap. 13.1 & 13.2)** |
| [`L33569`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33569) | **4B. ASYNCHRONE BLENDER-BOTANIK-HYDRATION (6 ARTEN x 15 VARIANTEN x LOD0/LOD1)** |
| [`L34979`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34979) | **4C. ASYNCHRONE MESOPOTAMIA-CITY-KIT-HYDRATION & 4-STUFEN-LOD (0..3000 m)** |
| [`L35988`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35988) | **4D. ASYNCHRONE SHIPYARD-INDUSTRY-KIT-HYDRATION & 4-STUFEN-LOD (0..3000 m)** |
| [`L36460`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36460) | **4E. ASYNCHRONE MENSCHEN-KIT v2.1 HYDRATION (8 NOAH-HEROES + 45 BÜRGER-VARIANTEN)** |
| [`L39110`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39110) | **3. Exakte Höhen-Synchronisation & Ausblenden des schwarzen seaGrid** |
| [`L42757`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42757) | **SYSTEM 1 (aPathType = 0.0): Vordere Frischluft-Schachtkammer & Erdregister |ZUL.|** |
| [`L42844`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42844) | **SYSTEM 2 (aPathType = 1.0 & 1.5): Stall-Durchstroemung & echte Tuer-Durchtritte** |
| [`L42886`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42886) | **SYSTEM 3 (aPathType = 2.0): Thermik, 1-Elle-Silospalt, Badgir-Lee-Kammer & Zohar** |
| [`L43059`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43059) | **SYSTEM 4 (aPathType = 3.0): Offenes 9x8-Ellen-Seitentor S7** |
| [`L50583`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L50583) | **Screen-Space Contact Shadows (SSCS, Half-Res Depth, Desktop Tier 0/1, WebGL1)** |
| [`L52771`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52771) | **SUITE 1: 1. Ellen-Kanon, EN 338 & Clean Architecture (T01–T07)** |
| [`L52820`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52820) | **SUITE 2: 2. Hydrostatik, Massenbilanz & Schwimmstabilität (T08–T18)** |
| [`L52906`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52906) | **SUITE 3: 3. Wellenkinematik & 6-DOF-Hydrodynamik (T19–T30)** |
| [`L52985`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52985) | **SUITE 4: 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik (T31–T53)** |
| [`L53218`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53218) | **SUITE 5: 5. 371-Tage-Chronik, Ermüdung & Instandhaltung (T54–T56)** |
| [`L53260`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53260) | **SUITE 6: 6. Holz-Stein-Maschinenbau, Silos & Einbauten (T57–T71)** |
| [`L53362`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53362) | **SUITE 7: 7. Meteorologie, Bauphysik & Veterinär-Physiologie (T72–T92)** |
| [`L53538`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53538) | **SUITE 8: 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität (T93–T101)** |

---

## 4. 3D-Baugruppen

### 4.1 Werftplatz & Trockendock (`buildShipyard3D`)
> Bereich: **Zeile 25118 bis 37160** (Funktion `Arche.Environment.buildShipyard3D`)

| Zeile | Typ | Baugruppe / Eigenschaft | Details |
|:-----:|:---:|:------------------------|:--------|
| [`L25122`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25122) | `userData` | **shipyardGroup.userData.cribbingBlocks** | `[];` |
| [`L25123`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25123) | `userData` | **shipyardGroup.userData.pitchPits** | `[];` |
| [`L25135`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25135) | `userData` | **shipyardGroup.userData.heightMapTex** | `bakedSy.tex;` |
| [`L25138`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25138) | `Abschnitt` | **1. Topografisches Trockendock-Becken & Quellgebirge (1600 x 1600 m, 240 x 240 Segmente)** | `` |
| [`L25164`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25164) | `userData` | **shipyardGroup.userData.basinMesh** | `terrainMesh;` |
| [`L25197`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25197) | `userData` | **shipyardGroup.userData.horizonRingMesh** | `syHorizon.mesh;` |
| [`L25198`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25198) | `userData` | **shipyardGroup.userData.horizonMat** | `syHorizon.mat;` |
| [`L25332`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25332) | `userData` | **shipyardGroup.userData.waterAquaMat** | `waterAquaMat;` |
| [`L25359`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25359) | `userData` | **shipyardGroup.userData.basaltMasonryMat** | `basaltMat;` |
| [`L25374`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25374) | `userData` | **shipyardGroup.userData.aqueductFlowMat** | `aqueductFlowMat;` |
| [`L25393`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25393) | `userData` | **shipyardGroup.userData.canalBedMat** | `canalBedMat;` |
| [`L25433`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25433) | `userData` | **shipyardGroup.userData.canalWaterBedMat** | `canalWaterBedMat;` |
| [`L25574`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25574) | `userData` | **shipyardGroup.userData.riverWaterMat** | `riverWaterMat;` |
| [`L25597`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25597) | `userData` | **shipyardGroup.userData.flagstoneMat** | `flagstoneMat;` |
| [`L25615`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25615) | `userData` | **shipyardGroup.userData.lapisFriezeMat** | `lapisFriezeMat;` |
| [`L25628`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25628) | `userData` | **shipyardGroup.userData.ochreAwningMat** | `ochreAwningMat;` |
| [`L25679`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25679) | `userData` | **shipyardGroup.userData.shipyardKitPlacements** | `shipyardKitPlacements;` |
| [`L25680`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25680) | `userData` | **shipyardGroup.userData.shipyardKitDynamic** | `shipyardKitDynamic;` |
| [`L25681`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25681) | `userData` | **shipyardGroup.userData.procShipyardMeshes** | `procShipyardMeshes;` |
| [`L25730`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25730) | `Abschnitt` | **3. Die 60-Ellen-Beladerampe zum Seitentor (Backbord @ X = -5.0 m)** | `` |
| [`L25753`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25753) | `userData` | **shipyardGroup.userData.mainRampMesh** | `deckMesh;` |
| [`L25817`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25817) | `Abschnitt` | **3. Animierte Beladungs-Karawane vor der Flut (boardingGroup)** | `` |
| [`L25821`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25821) | `userData` | **shipyardGroup.userData.boardingGroup** | `boardingGroup;` |
| [`L25823`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25823) | `userData` | **shipyardGroup.userData.boardingWalkers** | `boardingWalkers;` |
| [`L25896`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25896) | `userData` | **shipyardGroup.userData.caravanMeta** | `caravanMeta;` |
| [`L25965`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25965) | `userData` | **shipyardGroup.userData.caravanInstMesh** | `caravanInstMesh;` |
| [`L26004`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26004) | `userData` | **shipyardGroup.userData.shipyardBirdsInstMesh** | `shipyardBirdsInstMesh;` |
| [`L26007`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26007) | `userData` | **shipyardGroup.userData.impactFX** | `Arche.Fauna.createGroundImpactFX(shipyardGroup, 64, 56, false);` |
| [`L26015`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26015) | `userData` | **shipyardGroup.userData.bunkeringGroup** | `bunkeringGroup;` |
| [`L26017`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26017) | `userData` | **shipyardGroup.userData.bunkeringWalkers** | `bunkeringWalkers;` |
| [`L26029`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26029) | `userData` | **shipyardGroup.userData.sackMat** | `sackMat;` |
| [`L26153`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26153) | `Abschnitt` | **4. Zugbrücken-Klappe (drawbridgeFlapGroup)** | `` |
| [`L26181`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26181) | `userData` | **shipyardGroup.userData.bronzeToolMat** | `bronzeToolMat;` |
| [`L26188`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26188) | `userData` | **shipyardGroup.userData.smithyMetalMat** | `smithyMetalMat;` |
| [`L26227`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26227) | `userData` | **shipyardGroup.userData.mudbrickMat** | `mudbrickMat;` |
| [`L26242`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26242) | `userData` | **shipyardGroup.userData.reedThatchMat** | `reedThatchMat;` |
| [`L26252`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26252) | `userData` | **shipyardGroup.userData.dryWorkers** | `[];` |
| [`L26254`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26254) | `userData` | **shipyardGroup.userData.dryWorkerPlacements** | `_dryWorkerPlacements;` |
| [`L26296`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26296) | `userData` | **shipyardGroup.userData.scaffolds** | `[];` |
| [`L26632`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26632) | `userData` | **shipyardGroup.userData.craneWinchInstMeshes** | `_winchInstMeshes;` |
| [`L26633`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26633) | `userData` | **shipyardGroup.userData.craneOxInst** | `_craneOxInst;` |
| [`L26634`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26634) | `userData` | **shipyardGroup.userData.craneOxLocals** | `_craneOxLocals;` |
| [`L26645`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26645) | `userData` | **shipyardGroup.userData.craneHoistGroups** | `craneHoistGroups;` |
| [`L26646`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26646) | `userData` | **shipyardGroup.userData.craneWinchRotors** | `craneWinchRotors;` |
| [`L26648`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26648) | `Abschnitt` | **7. Kopher-Pechsiederei (3 Rundöfen mit glühendem Bad, Pechsiedern & Kalfater-Werkzeuglager)** | `` |
| [`L26843`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26843) | `userData` | **shipyardGroup.userData.smithyEmberMat** | `smithyEmberMat;` |
| [`L26855`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26855) | `userData` | **shipyardGroup.userData.terracottaMat** | `terracottaMat;` |
| [`L26976`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26976) | `userData` | **shipyardGroup.userData.hayMat** | `hayMat;` |
| [`L27011`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27011) | `Abschnitt` | **10. Kapitel 13: Holzriese & Rollenbahn** | `` |
| [`L27109`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27109) | `Kapitel 13 Baugruppe` | **BAUGRUPPE 1: Baumfäll-Szene im Primärwald & Rollenträger-Knechte (Kap. 13.1)** | `` |
| [`L27118`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27118) | `Abschnitt` | **1. Stehender 22-m-Zedernriese (D = 1.56 m) — nutzt leichtes Lambert-Foliage-Material statt separatem 250-Zeilen-Legacy-Programm!** | `` |
| [`L27209`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27209) | `Abschnitt` | **3. Seilzug in der Krone + Umlenkrolle + 4 Zugochsen als 2 Doppelgespanne (Kettenlinie mit Durchhang)** | `` |
| [`L27259`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27259) | `Abschnitt` | **4. Nachbar-Baumstumpf (-139.2, -96.8) & waagerecht am Boden liegender 20-m-Zedernstamm ([-138.0, -96.0] bis [-122.0, -84.0]) mit 3D-POM-Zedernborke** | `` |
| [`L27361`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27361) | `userData` | **shipyardGroup.userData.fellingSceneGroup** | `fellingSceneGroup;` |
| [`L27365`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27365) | `Kapitel 13 Baugruppe` | **BAUGRUPPE 2: Göpel-Sägewerk, drehender Rotor, Kurbelschleife & Sägegruben (Kap. 13.1)** | `` |
| [`L27376`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27376) | `Abschnitt` | **1. Basalt-Bruchsteinring (R = 4.0 m) auf dem ebenen +2.80 m Plateau** | `` |
| [`L27384`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27384) | `Abschnitt` | **2. Feststehendes Eichen-Galgenportal & Basalt-Spurlager über dem Göpel** | `` |
| [`L27394`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27394) | `Abschnitt` | **3. Drehbare Untergruppe: sawmillCapstanRotor (Königswelle, Kammrad & Joche gebatcht + 4 gehörnte Zugochsen)** | `` |
| [`L27446`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27446) | `userData` | **shipyardGroup.userData.sawmillCapstanRotor** | `sawmillCapstanRotor;` |
| [`L27448`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27448) | `Abschnitt` | **4. Drehende Vorgelegewelle mit 8er-Stockritzel, Schwungrad & Kurbelzapfen (sawDriveShaftRotor)** | `` |
| [`L27455`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27455) | `userData` | **shipyardGroup.userData.sawdustMat** | `sawdustMat;` |
| [`L27495`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27495) | `userData` | **shipyardGroup.userData.sawDriveShaftRotor** | `sawDriveShaftRotor;` |
| [`L27497`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27497) | `Abschnitt` | **5. Lagerung der Vorgelegewelle: Oberer Längsträger über der Ochsenbahn (0 % Spur-Kollision!) + Außen-Lagerbock bei x = sx0 + 4.65** | `` |
| [`L27533`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27533) | `Abschnitt` | **6. Vertikales Sägegatter mit separat gelenkter Pleuelstange (Kurbelschleife)** | `` |
| [`L27550`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27550) | `userData` | **shipyardGroup.userData.sawFrame** | `sawFrameMesh;` |
| [`L27551`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27551) | `userData` | **shipyardGroup.userData.sawFrameBaseZ** | `sz0 + 1.2;` |
| [`L27563`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27563) | `userData` | **shipyardGroup.userData.sawPitmanGroup** | `sawPitmanGroup;` |
| [`L27564`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27564) | `userData` | **shipyardGroup.userData.sawPitmanBaseZ** | `sz0 + 1.82;` |
| [`L27565`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27565) | `userData` | **shipyardGroup.userData.sawPitmanCenterY** | `sy0;` |
| [`L27566`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27566) | `userData` | **shipyardGroup.userData.sawCrankCenterZ** | `sz0 + 2.62;` |
| [`L27669`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27669) | `userData` | **shipyardGroup.userData.sawPitGroup** | `sawPitGroup;` |
| [`L27673`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27673) | `Kapitel 13 Baugruppe` | **BAUGRUPPE 3: 4 Holzkohlemeiler, Tubal-Kain-Schmiede & 9 Rauchsäulen (Kap. 13.1 & 13.2)** | `` |
| [`L27689`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27689) | `userData` | **shipyardGroup.userData.meilerDomeMat** | `meilerDomeMat;` |
| [`L27699`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27699) | `userData` | **shipyardGroup.userData.meilerHotMat** | `meilerHotMat;` |
| [`L27747`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27747) | `userData` | **shipyardGroup.userData.smokeMat** | `smokeMat;` |
| [`L27774`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27774) | `userData` | **shipyardGroup.userData.smokePlumesGroup** | `smokePlumesGroup;` |
| [`L27775`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27775) | `userData` | **shipyardGroup.userData.smokePuffs** | `smokePuffs;` |
| [`L27791`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27791) | `userData` | **shipyardGroup.userData.smithyAnvilMat** | `smithyAnvilMat;` |
| [`L27890`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27890) | `userData` | **shipyardGroup.userData.smithyToolsGroup** | `smithyToolsGroup;` |
| [`L27893`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27893) | `Abschnitt` | **13. Kapitel 13: Frischwasser-Aquädukt & Raubtier-Rollkäfige** | `` |
| [`L28152`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28152) | `userData` | **shipyardGroup.userData.cityKitPlacements** | `cityKitPlacements;` |
| [`L28153`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28153) | `userData` | **shipyardGroup.userData.roadKitProps** | `roadKitProps;` |
| [`L28154`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28154) | `userData` | **shipyardGroup.userData.procCityMeshes** | `procCityMeshes;` |
| [`L28897`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28897) | `userData` | **shipyardGroup.userData.temenosKitPlacements** | `temenosKitPlacements;` |
| [`L28898`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28898) | `userData` | **shipyardGroup.userData.procTemenosMeshes** | `procTemenosMeshes;` |
| [`L28940`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28940) | `Abschnitt` | **1. Hero-Ziggurat ("hero_ziggurat_ur") exakt auf Prozessionsachse x=210 zum Prunktor ausgerichtet (Dreifachtreppe -> -Y, nach hinten +6.5m verlängert -> Rückwand Y=+8.50m, 6.50m frei bis Nordmauer Y=+15.0m!)** | `` |
| [`L28946`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28946) | `Abschnitt` | **2. Hero-Temenos-Prunktor ("hero_temenos_gate") exakt auf der Prozessionsachse (210, -38)** | `` |
| [`L28952`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28952) | `Abschnitt` | **3. Hero-Temenos-Innenmauer ("hero_temenos_wall_seg", 6m-Modul mit -0.35m Schürze -> 0 Fundament-Z-Fighting!)** | `` |
| [`L28983`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28983) | `Abschnitt` | **4. Hero-Nebengebäude ("hero_temple_annex_01" Schatzhaus & "hero_temple_annex_02" Priester-/Archivhaus, Portikus +X zum Tempelhof!)** | `` |
| [`L28998`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28998) | `Abschnitt` | **5. Zwei monumentale 3D-Abzu-Tempelteiche ("hero_abzu_pond" + "abzu_water_surface") symmetrisch links/rechts der Prozessionsachse!** | `` |
| [`L29020`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29020) | `Abschnitt` | **6. Durchgehendes Travertin-Prozessionspflaster ("temple_paving_slab") vom Prunktor zum Vorplatz-Altar & Zikkurat-Treppe + Querachsen** | `` |
| [`L29033`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29033) | `Abschnitt` | **7. Vorplatz-Heiligtum: Monumentaler Hornaltar, 2 Sumerische Stelen & 6 Bronze-Feuerständer (castShadow = false)** | `` |
| [`L29052`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29052) | `Abschnitt` | **8. Üppiger Heiliger Hain & Tempelgärten: Gemauerte Hochbeete, Schatten-Pergolen, Tempel-Zypressen & Granatapfelbäume!** | `` |
| [`L29180`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29180) | `userData` | **shipyardGroup.userData.blenderOrnamentalSpecs** | `blenderOrnamentalSpots;` |
| [`L29535`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29535) | `userData` | **shipyardGroup.userData.organicRoadMesh** | `orgRoadMesh;` |
| [`L29536`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29536) | `userData` | **shipyardGroup.userData.organicRoadMat** | `orgRoadMat;` |
| [`L29554`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29554) | `userData` | **shipyardGroup.userData.roadMesh** | `roadMesh;` |
| [`L29555`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29555) | `userData` | **shipyardGroup.userData.roadMeshOrigMat** | `flagstoneMat;` |
| [`L29738`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29738) | `Abschnitt` | **1. Nord-Vorstadt (außerhalb Nord-Königstor bei y=+36..+52)** | `` |
| [`L29741`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29741) | `Abschnitt` | **2. Süd-Vorstadt (außerhalb Süd-Karawanentor bei y=-136..-162)** | `` |
| [`L29744`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29744) | `Abschnitt` | **3. Ostufer-Brückenkopf & Karawanserei (x=272..294, y=-68..-28)** | `` |
| [`L30208`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30208) | `userData` | **shipyardGroup.userData.cityBoats** | `cityBoats;` |
| [`L30263`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30263) | `userData` | **shipyardGroup.userData.cityWalkers** | `cityWalkers;` |
| [`L30518`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30518) | `Abschnitt` | **1. Ur-Schinar Süd & Südwest-Schwemmland (10 große Parzellen)** | `` |
| [`L30529`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30529) | `Abschnitt` | **2. Ur-Ostufer / Euphrat-Ostebene gegenüber der Metropole (10 weite Parzellen)** | `` |
| [`L30540`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30540) | `Abschnitt` | **3. Nisaba-Kornkammer / Südwest-Ebene (10 weite Parzellen)** | `` |
| [`L30551`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30551) | `Abschnitt` | **4. Eridu-Lagunengürtel / Südost-Ebene (8 große Parzellen)** | `` |
| [`L30560`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30560) | `Abschnitt` | **5. Girsu-Kanalauen / Ost-Ebene (8 weite Parzellen)** | `` |
| [`L30569`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30569) | `Abschnitt` | **6. Sippar & Nord-Euphrattal (6 große Parzellen)** | `` |
| [`L30576`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30576) | `Abschnitt` | **7. Larsam-Südoase / Süd-Weide & Getreidegürtel (6 weite Parzellen)** | `` |
| [`L30853`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30853) | `userData` | **shipyardGroup.userData.procCropInstMesh** | `cropInstMesh;` |
| [`L30854`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30854) | `userData` | **shipyardGroup.userData.blenderCropSpecs** | `{` |
| [`L30968`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30968) | `Abschnitt` | **1. Ur-Schinar Süd & SW (12)** | `` |
| [`L30975`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30975) | `Abschnitt` | **2. Ur-Ostufer gegenüber Metropole (12)** | `` |
| [`L30982`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30982) | `Abschnitt` | **3. Nisaba Kornkammer (12)** | `` |
| [`L30989`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30989) | `Abschnitt` | **4. Eridu Lagunengürtel (8)** | `` |
| [`L30994`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30994) | `Abschnitt` | **5. Girsu Ost-Ebene (8)** | `` |
| [`L30999`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30999) | `Abschnitt` | **6. Sippar & Nord-Euphrattal (6)** | `` |
| [`L31003`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31003) | `Abschnitt` | **7. Larsam Südoase (6)** | `` |
| [`L31120`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31120) | `userData` | **shipyardGroup.userData.farmInsts** | `{` |
| [`L31132`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31132) | `userData` | **shipyardGroup.userData.farmMovers** | `farmMovers;` |
| [`L31196`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31196) | `userData` | **shipyardGroup.userData.shadufInsts** | `shadufInsts;` |
| [`L31197`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31197) | `userData` | **shipyardGroup.userData.shadufBeams** | `shadufBeams;` |
| [`L31236`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31236) | `userData` | **shipyardGroup.userData.waterWheels** | `waterWheels;` |
| [`L31250`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31250) | `userData` | **shipyardGroup.userData.waterFoamMat** | `waterFoamMat;` |
| [`L31291`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31291) | `userData` | **shipyardGroup.userData.waterFoamInstMesh** | `waterFoamInstMesh;` |
| [`L31292`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31292) | `userData` | **shipyardGroup.userData.waterFoamNodes** | `foamNodes;` |
| [`L31293`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31293) | `userData` | **shipyardGroup.userData.waterFoamWakeStart** | `wakeSlotStart;` |
| [`L31308`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31308) | `userData` | **shipyardGroup.userData.cityBuildingShadowsInstMesh** | `bldgShadowInst;` |
| [`L31377`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31377) | `userData` | **shipyardGroup.userData.oarsmanInst** | `oarInst;` |
| [`L31403`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31403) | `userData` | **shipyardGroup.userData.magurInstMeshes** | `boatParts.map(p => p.inst);` |
| [`L31404`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31404) | `userData` | **shipyardGroup.userData._magurAllCount** | `_magurAll.length;` |
| [`L31405`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31405) | `userData` | **shipyardGroup.userData._magurLogCount** | `_magurLogs.length;` |
| [`L31406`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31406) | `userData` | **shipyardGroup.userData._magurCargoCount** | `_magurCargo.length;` |
| [`L31407`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31407) | `userData` | **shipyardGroup.userData.updateMagurBoatMatrix** | `(bt, mat4) => {` |
| [`L31520`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31520) | `userData` | **shipyardGroup.userData.cityWalkerInstMeshes** | `cityWalkerInstMeshes;` |
| [`L31539`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31539) | `userData` | **shipyardGroup.userData.smokeInstMesh** | `smokeInst;` |
| [`L31647`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31647) | `userData` | **shipyardGroup.userData.boulderMat** | `boulderMat;` |
| [`L31705`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31705) | `userData` | **shipyardGroup.userData.boulderInstMesh** | `boulderInstMesh;` |
| [`L31727`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31727) | `userData` | **shipyardGroup.userData.logYardMat** | `logYardMat;` |
| [`L31767`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31767) | `userData` | **shipyardGroup.userData.logYardInstMesh** | `logYardInstMesh;` |
| [`L31952`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31952) | `userData` | **shipyardGroup.userData.steppeGrassInstMesh** | `steppeGrassInstMesh;` |
| [`L31953`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31953) | `userData` | **shipyardGroup.userData.blenderGrassSpecs** | `{ count: gPlaced, transforms: gPlaceTf, kind: gPlaceKind, colors:` |
| [`L32138`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32138) | `userData` | **shipyardGroup.userData.steppeShrubInstMesh** | `shrubInstMeshes[0];` |
| [`L32139`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32139) | `userData` | **shipyardGroup.userData.shrubInstMeshes** | `shrubInstMeshes;` |
| [`L32140`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32140) | `userData` | **shipyardGroup.userData.procShrubMeshes** | `shrubInstMeshes.slice();` |
| [`L32175`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32175) | `userData` | **shipyardGroup.userData.stumpBarkMat** | `stumpBarkMat;` |
| [`L32176`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32176) | `userData` | **shipyardGroup.userData.stumpCutMat** | `stumpCutMat;` |
| [`L32225`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32225) | `userData` | **shipyardGroup.userData.treeStumps** | `stumpsGroup;` |
| [`L32734`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32734) | `userData` | **shipyardGroup.userData.treesGroup** | `treesGroup;` |
| [`L32735`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32735) | `userData` | **shipyardGroup.userData.procTreeInstMeshes** | `allTreeInstMeshes.slice();` |
| [`L32736`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32736) | `userData` | **shipyardGroup.userData.blenderForestPlacements** | `{` |
| [`L32771`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32771) | `userData` | **shipyardGroup.userData.treeShadowInstMesh** | `_syTreeShadInst;` |
| [`L32774`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32774) | `userData` | **shipyardGroup.userData.forestTrunksInstMesh** | `forestTrunksInstMesh;` |
| [`L32775`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32775) | `userData` | **shipyardGroup.userData.allTreeInstMeshes** | `allTreeInstMeshes;` |
| [`L33045`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33045) | `Abschnitt` | **1. Bäume: Echtes 4-Stufen-LOD (Desktop: 150m / 500m / 1500m / 3000m, Werft & Ararat!)** | `` |
| [`L33308`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33308) | `Abschnitt` | **2. Prüfe die Strauch-Meshes (shrubInstMeshes — bis 640 m & hartes Frustum-Culling)** | `` |
| [`L33359`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33359) | `Abschnitt` | **3. Hydrierte Blender-Unterholz-, Gras-/Schilf-, Agrar- & Tempelzierbotanik-Gruppen (Werft & Ararat + Frustum-Culling)** | `` |
| [`L33519`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33519) | `Abschnitt` | **4. Frustum- & Distanz-Culling für Werft-Handwerker (dryWorkers) & Stadtbewohner-Zone (Ur-Schinar)** | `` |
| [`L34492`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34492) | `Abschnitt` | **1. Sträucher & Euphrat-Schilf/Papyrus aus procShrubMeshes** | `` |
| [`L34521`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34521) | `Abschnitt` | **2. Steppengras & Hochgras aus blenderGrassSpecs** | `` |
| [`L34544`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34544) | `Abschnitt` | **3. Mesopotamische Kulturpflanzen & Weinreben aus blenderCropSpecs** | `` |
| [`L34565`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34565) | `Abschnitt` | **4. Tempel-, Hofgarten-, Terrakotta-Kübel- & Lotus-Zierbotanik** | `` |
| [`L34652`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34652) | `Abschnitt` | **1. Ararat-Bäume nach (species, stage, varIdx) bündeln & auf 4-LOD-Pools (150/500/1500/3000m) mappen** | `` |
| [`L34810`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34810) | `Abschnitt` | **2. Ararat Sträucher, Schilf & Pioniergras als LOD-gepoolte ExtraGroups (mit uSproutGrowth & Frustum-Culling)** | `` |
| [`L35612`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35612) | `Abschnitt` | **1. Trim-Material: teilt arche_world_trim_unified_v1 (0 neue Shader-Programme!) + glühende Altarkohle via emissiveMap!** | `` |
| [`L35621`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35621) | `Abschnitt` | **2. Botanik-Material: teilt arche_blender_botany_v5_fol (0 neue Shader-Programme!) mit identischer DUMMY_TEX-Signatur!** | `` |
| [`L35668`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35668) | `Abschnitt` | **3. Abzu-Wasseroberfläche: 1 gemeinsames reguläres Mesh mit ud.waterAquaMat (0 neue Shader-Programme, 1 Draw-Call, 0% Z-Fighting!)** | `` |
| [`L35731`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35731) | `Abschnitt` | **4. InstancedMesh-Pools für alle 14 Temenos-Architektur-, Garten- & Baum-Module (4 LODs: 150/500/1500/3000 m)** | `` |
| [`L36639`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36639) | `Abschnitt` | **1. Alle 8 Mitglieder von Noahs Familie am Ararat-Altar (1:1 Meter-Skala, scale = 1.0, sauberer Bodenkontakt!)** | `` |
| [`L37143`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37143) | `Abschnitt` | **5. Kompletter Neuaufbau des Ararat-Landeplatzes (Arche.Environment.buildAraratLandingSite3D)** | `` |

### 4.2 Ararat-Landeplatz (`buildAraratLandingSite3D`)
> Bereich: **Zeile 37161 bis 39204** (Funktion `Arche.Environment.buildAraratLandingSite3D`)

| Zeile | Typ | Baugruppe / Eigenschaft | Details |
|:-----:|:---:|:------------------------|:--------|
| [`L37165`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37165) | `userData` | **araratGroup.userData.isBuilt** | `true;` |
| [`L37166`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37166) | `userData` | **araratGroup.userData.blenderCharactersHydrated** | `false;` |
| [`L37167`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37167) | `userData` | **araratGroup.userData.saddleMesh** | `null;` |
| [`L37168`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37168) | `userData` | **araratGroup.userData.altarCoals** | `null;` |
| [`L37169`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37169) | `userData` | **araratGroup.userData.disembarkRampMesh** | `null;` |
| [`L37181`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37181) | `userData` | **araratGroup.userData.heightMapTex** | `bakedAra.tex;` |
| [`L37184`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37184) | `Abschnitt` | **1. Integriertes Hochgebirgs- & Sattel-Mesh (1.400 x 1.400 m, 208 x 208 Segmente mit zentrierter Auflösungs-Verdichtung für glatte Gipfelgrate & bündigen Kielsattel)** | `` |
| [`L37212`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37212) | `userData` | **araratGroup.userData.saddleMesh** | `terrainMesh;` |
| [`L37240`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37240) | `userData` | **araratGroup.userData.horizonRingMesh** | `araHorizon.mesh;` |
| [`L37241`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37241) | `userData` | **araratGroup.userData.horizonMat** | `araHorizon.mat;` |
| [`L37307`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37307) | `userData` | **araratGroup.userData.basaltCragsInstMesh** | `cragInst;` |
| [`L37429`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37429) | `userData` | **araratGroup.userData.waterfallGroup** | `waterfallGroup;` |
| [`L37430`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37430) | `userData` | **araratGroup.userData.waterfallUniforms** | `waterfallUniforms;` |
| [`L37432`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37432) | `Abschnitt` | **2. Fels-, Holz-, Feuer- & Bronzezeit-Materialien (alle WebGL1 AAA-gekoppelt & Thermo-/Struktur-fähig)** | `` |
| [`L37491`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37491) | `Abschnitt` | **3. Ausschiffungs-Steg & 4-stufiger Baufortschritt (rampStages) mit Catenary-Hanfseilen & Zimmermannsholz** | `` |
| [`L37595`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37595) | `userData` | **araratGroup.userData.rampCarpenterMeshes** | `rampCarpenterMeshes;` |
| [`L37746`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37746) | `userData` | **araratGroup.userData.rampStages** | `{` |
| [`L37752`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37752) | `userData` | **araratGroup.userData.disembarkRampMesh** | `gangwayDeck;` |
| [`L37758`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37758) | `Abschnitt` | **4. Großer Zyklopischer Dankopfer-Altar (Gen 8,20 / Ex 20,25), Opferfeuer (~600°C Thermo) & Noahs gesamte Familie (8 Personen)** | `` |
| [`L37829`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37829) | `userData` | **araratGroup.userData.altarStoneGroup** | `altarStoneGroup;` |
| [`L37843`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37843) | `userData` | **araratGroup.userData.altarCoals** | `coalMesh;` |
| [`L37867`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37867) | `userData` | **araratGroup.userData.uAltarFireThermo** | `uAltarFireThermo;` |
| [`L37868`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37868) | `userData` | **araratGroup.userData.uAltarFlicker** | `uAltarFlicker;` |
| [`L37894`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37894) | `userData` | **araratGroup.userData.altarEmberGlow** | `altarEmberGlow;` |
| [`L37901`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37901) | `userData` | **araratGroup.userData.altarFlickerLight** | `altarFlickerLight;` |
| [`L37903`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37903) | `Abschnitt` | **1. Volumetrisches fBm-Schwarzkörper-Opferfeuer (7 gekreuzte Flammen-Flächen = 1 Draw-Call, WebGL1-konform)** | `` |
| [`L38026`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38026) | `userData` | **araratGroup.userData.altarFlames** | `altarFlames;` |
| [`L38028`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38028) | `Abschnitt` | **2. Aufsteigende Funken & Glut-Asche (45 Funken in 1 THREE.Points Draw-Call, rein im Shader animiert)** | `` |
| [`L38093`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38093) | `userData` | **araratGroup.userData.altarSparks** | `altarSparks;` |
| [`L38095`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38095) | `Abschnitt` | **3. Weicher prozeduraler Opferrauch (Noise-Alpha-Billboards, keine harten Kugel-Silhouetten!)** | `` |
| [`L38174`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38174) | `userData` | **araratGroup.userData.altarSmokePuffs** | `altarSmokePuffs;` |
| [`L38209`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38209) | `userData` | **araratGroup.userData.altarFamilyEntries** | `altarFamilyEntries;` |
| [`L38210`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38210) | `userData` | **araratGroup.userData.altarGroup** | `altarGroup;` |
| [`L38213`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38213) | `Abschnitt` | **5. Kreativ-Highlight: Bronzezeitliches Basislager am Stegfuß (Terrakotta-Amphoren, Zedernkiste, Werkzeuge, Hanftau — mat zuerst!)** | `` |
| [`L38269`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38269) | `userData` | **araratGroup.userData.campGroup** | `campGroup;` |
| [`L38292`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38292) | `userData` | **araratGroup.userData.svalbardPlotGroup** | `svalbardPlotGroup;` |
| [`L38295`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38295) | `Abschnitt` | **6. Kreativ-Highlight: Schimmernde Gletscher-Schmelzwasser-Tümpel & Südtal-Tränkelagunen** | `` |
| [`L38328`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38328) | `userData` | **araratGroup.userData.meltwaterGroup** | `meltwaterGroup;` |
| [`L38367`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38367) | `userData` | **araratGroup.userData.strandedMatsGroup** | `strandedMatsGroup;` |
| [`L38368`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38368) | `userData` | **araratGroup.userData.matCentersAra** | `matCentersAra;` |
| [`L38371`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38371) | `Abschnitt` | **7. Weiträumige Auswanderungs-Korridore & Herden-Verteilung über das gesamte Ararat-Massiv (Kap. 14.5)** | `` |
| [`L38517`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38517) | `userData` | **araratGroup.userData.plateauQuadInstMesh** | `plateauQuadInstMesh;` |
| [`L38518`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38518) | `userData` | **araratGroup.userData.plateauMovers** | `plateauMovers;` |
| [`L38519`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38519) | `userData` | **araratGroup.userData.plateauFaunaGroup** | `plateauFaunaGroup;` |
| [`L38522`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38522) | `Abschnitt` | **8. Kreativ-Highlight: Taube mit Ölzweig (0), Rabe (1) + 42-Vögel-Schwarm aus Himmelsdeck / Zohar in freier Bergthermik (Kap. 14.5 Phase 1)** | `` |
| [`L38562`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38562) | `userData` | **araratGroup.userData.avianFlyInstMesh** | `avianFlyInstMesh;` |
| [`L38596`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38596) | `userData` | **araratGroup.userData.doveSprigGroup** | `doveSprigGroup;` |
| [`L38603`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38603) | `userData` | **araratGroup.userData.doveHeroAnchor** | `doveHeroAnchor;` |
| [`L38618`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38618) | `Abschnitt` | **9. Kreativ-Highlight: Regenbogen-Bundesbogen hoch & weit am Himmel HINTER dem Ararat-Massiv (Gen 9,13, 0% Bergschnitt!)** | `` |
| [`L38684`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38684) | `userData` | **araratGroup.userData.rainbowArcMesh** | `rainbowArcMesh;` |
| [`L38685`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38685) | `userData` | **araratGroup.userData.rainbowUniforms** | `rainbowUniforms;` |
| [`L38689`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38689) | `userData` | **araratGroup.userData.impactFX** | `Arche.Fauna.createGroundImpactFX(araratGroup, 64, 56, true);` |
| [`L38857`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38857) | `userData` | **araratGroup.userData.sproutGrassMesh** | `araratSproutGrassInstMesh;` |
| [`L38860`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38860) | `Abschnitt` | **11. Echte botanische Werft-Vegetation + Ovoli-Olivenstümpfe & Schilf auf Ararat (Kap. 15.3–15.6)** | `` |
| [`L38977`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38977) | `userData` | **araratGroup.userData.procAraTreeMeshes** | `_procAraTreeMeshes;` |
| [`L38978`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38978) | `userData` | **araratGroup.userData.blenderAraratHydrated** | `false;` |
| [`L38979`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38979) | `userData` | **araratGroup.userData.blenderAraratSpecs** | `[` |
| [`L39040`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39040) | `userData` | **araratGroup.userData.procAraAllMeshes** | `floraInstMeshes.slice();` |
| [`L39041`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39041) | `userData` | **araratGroup.userData.blenderAraratSpecs** | `araratGroup.userData.blenderAraratSpecs.concat(araShrubSpecs);` |
| [`L39064`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39064) | `userData` | **araratGroup.userData.ovoliShootsGroup** | `ovoliShootsGroup;` |
| [`L39095`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39095) | `userData` | **araratGroup.userData.treeShadowInstMesh** | `_araTreeShadInst;` |
| [`L39099`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39099) | `userData` | **araratGroup.userData.oliveSaplingsGroup** | `araratOliveSaplingsGroup;` |
| [`L39100`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39100) | `userData` | **araratGroup.userData.floraInstMeshes** | `floraInstMeshes;` |
| [`L39101`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39101) | `userData` | **araratGroup.userData.oliveSaplings** | `[];` |
| [`L39102`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39102) | `userData` | **araratGroup.userData.themedMats** | `themedMatsAra;` |
| [`L39110`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39110) | `Abschnitt` | **3. Exakte Höhen-Synchronisation & Ausblenden des schwarzen seaGrid** | `` |

---

## 5. Modul- & Top-Level-Funktionen

### 5.1 Arche.Procedural (Texturen, POM & Shader)

| Zeile | Funktion / Signatur |
|:-----:|:--------------------|
| [`L5259`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5259) | `Arche.Procedural.createInstantPlaceholderTex(r, g, b, repU = 1.0, repV = 1.0, isColor = true)` |
| [`L5278`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5278) | `Arche.Procedural.DUMMY_TEX(()` |
| [`L5460`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5460) | `Arche.Procedural.spawnMulticoreTexturePool()` |
| [`L5591`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5591) | `Arche.Procedural.buildWaterNormalTexture()` |
| [`L5636`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5636) | `Arche.Procedural.buildRoughnessTexture()` |
| [`L5675`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5675) | `Arche.Procedural.buildDetailMicroTexture(kind)` |
| [`L5779`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5779) | `Arche.Procedural.bindDetailUniforms(shader)` |
| [`L5824`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5824) | `Arche.Procedural.bindInteriorLightUniforms(shader)` |
| [`L5903`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5903) | `Arche.Procedural.attachCloseUpDetailLOD(mat, isPitchHull = false, isBarrelMat = false, isVolumetricBedding = false, isBasaltStone = false)` |
| [`L6294`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6294) | `Arche.Procedural.bindGpuShader(material, fixedMatId = 1)` |
| [`L6469`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6469) | `Arche.Procedural.bindEnvUniforms(shader)` |
| [`L6477`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6477) | `Arche.Procedural.injectEnvFogAndCloud(fragShader, worldPosExpr, applyCloudShadow = true, horizonShadowExpr = '')` |
| [`L6505`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6505) | `Arche.Procedural.bindMechPomShader(colorHex, mechType = 1)` |
| [`L6690`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6690) | `Arche.Procedural.cloneNoDeckClipMat(srcMat)` |
| [`L10474`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L10474) | `Arche.Procedural.buildBeddingAlphaShellTexture()` |
| [`L10559`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L10559) | `Arche.Procedural.buildVerticalHayFinTexture()` |
| [`L14737`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L14737) | `Arche.Procedural.setBucketFixturesWaveBMask(mask)` |
| [`L14783`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L14783) | `Arche.Procedural.updateInstancedBarrelsShader(ctx)` |
| [`L15760`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15760) | `Arche.Procedural.updateDrivetrainAndGalleyVisuals(ctx, fixRes, shiftState)` |
| [`L19320`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19320) | `Arche.Procedural.updateStormShutters3D(v_roof_kmh, mu_wind_rad, precip_mmh, ctx)` |
| [`L24366`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24366) | `Arche.Procedural.makeEnvMat(cacheKey, baseHex, rough, metal, fragExtraGLSL, options = {})` |
| [`L42705`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42705) | `Arche.Procedural.rebuildAirflow3DGeometry()` |
| [`L46513`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46513) | `Arche.Procedural.tempToHeatmapRGB(tempC)` |

### 5.2 Arche.Environment (Werft, Ararat & Botanik)

| Zeile | Funktion / Signatur |
|:-----:|:--------------------|
| [`L7052`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L7052) | `Arche.Environment.loadTerrainTextures()` |
| [`L7206`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L7206) | `Arche.Environment._decodeUint16PngToFloat32(arrayBuf, zMin, zMax)` |
| [`L7279`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L7279) | `Arche.Environment.syncBlenderWorlds3D()` |
| [`L7342`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L7342) | `Arche.Environment.loadBlenderWorldMaps(opts = {})` |
| [`L10764`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L10764) | `Arche.Environment.heightTexUniforms(()` |
| [`L19462`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19462) | `Arche.Environment.updateDeckSlicePlaneWorld()` |
| [`L21953`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21953) | `Arche.Environment.createZUpCylinderGeo(rTop, rBot, heightZ, segs = 12)` |
| [`L21960`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21960) | `Arche.Environment.addStrutBetweenPoints(parentGroup, p0, p1, rBot = 0.12, rTop = 0.12, mat = null, tooltipKey = null)` |
| [`L22017`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22017) | `Arche.Environment.evalRiverCenterX(y)` |
| [`L22023`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22023) | `Arche.Environment.evalRiverHalfWidth(y)` |
| [`L22028`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22028) | `Arche.Environment.evalRiverSurfaceZ(y)` |
| [`L22036`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22036) | `Arche.Environment.evalApproachRoadX(y)` |
| [`L22073`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22073) | `Arche.Environment.evalLakeLobeRadiusFrac(lake, x, y)` |
| [`L22083`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22083) | `Arche.Environment.evalLakeShorePoint(lake, ang, rFrac = 1.0)` |
| [`L22091`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22091) | `Arche.Environment.evalAlluvialLakeField(x, y)` |
| [`L22101`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22101) | `Arche.Environment.evalDistToPolyline(x, y, pts)` |
| [`L22115`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22115) | `Arche.Environment.evalCanalField(x, y)` |
| [`L22139`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22139) | `Arche.Environment._sampleBlenderHeightmapBilinear(hm, x, y)` |
| [`L22155`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22155) | `Arche.Environment.evalShipyardTerrainZ(x, y)` |
| [`L22305`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22305) | `Arche.Environment.evalAraratTerrainZ(x, y)` |
| [`L22904`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22904) | `Arche.Environment.getOrientalFoliageAtlasTex()` |
| [`L23118`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23118) | `Arche.Environment.pushLimb(buf, p0, p1, r0, r1, nSegs, rCol, gCol, bCol)` |
| [`L23176`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23176) | `Arche.Environment.pushFoliageCluster(buf, cx, cy, cz, rx, ry, rz, quadIdx, rCol, gCol, bCol, nCards = 9)` |
| [`L23235`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23235) | `Arche.Environment.pushPalmFrondRibbon(buf, spinePts, wStart, wMax, wEnd, rCol, gCol, bCol)` |
| [`L23297`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23297) | `Arche.Environment.createOrientalTreeGeo(speciesIdx, variantIdx)` |
| [`L23657`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23657) | `Arche.Environment.createOrientalShrubGeo(shrubType)` |
| [`L23751`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23751) | `Arche.Environment.getBotanyThicknessTex()` |
| [`L23782`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23782) | `Arche.Environment.applyOrientalFoliageShader(mat, options = {})` |
| [`L24595`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24595) | `Arche.Environment.createHorizonTerrainRing(opts)` |
| [`L24713`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24713) | `Arche.Environment.bakeTerrainHeightTex(evalLocalZFn, halfSpan = 3000.0, res = 256)` |
| [`L24749`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24749) | `Arche.Environment.getTreeShadowBlobTex()` |
| [`L24794`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24794) | `Arche.Environment.createProjectedTreeShadowsMesh(treesList, evalTerrainZFn, opts = {})` |
| [`L24944`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24944) | `Arche.Environment.createProjectedBuildingShadowsMesh(bldgBoxes, evalTerrainZFn, opts = {})` |
| [`L25066`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25066) | `Arche.Environment.evalShipyardHorizonZ(wx, wy, uRadOpt, isSkirtOpt)` |
| [`L25091`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25091) | `Arche.Environment.evalAraratHorizonZ(wx, wy, uRadOpt, isSkirtOpt)` |
| [`L25118`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25118) | `Arche.Environment.buildShipyard3D()` |
| [`L32825`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32825) | `Arche.Environment.updateVegetationLOD(cam, forceUpdate = false)` |
| [`L33921`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33921) | `Arche.Environment.registerBotanySpecies(speciesKey, opts = {})` |
| [`L33926`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33926) | `Arche.Environment.loadBotanyPlantPack(speciesKey, glbUrl, opts = {})` |
| [`L33940`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33940) | `Arche.Environment.applyBotanyShaderToObject(rootObj, opts = {})` |
| [`L33981`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33981) | `Arche.Environment.loadBlenderBotanyPacks()` |
| [`L34041`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34041) | `Arche.Environment._mergeShadowProxyGeo(parts)` |
| [`L34081`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34081) | `Arche.Environment._allocTreeShadowProxyPool(cap, archKey, refSp, packsMap, parentGrp, poolList, poolMap, meshAcc, tooltipKey, depthMat, namePrefix)` |
| [`L34119`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34119) | `Arche.Environment.hydrateBlenderForest3D(packsMap)` |
| [`L34355`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34355) | `Arche.Environment.hydrateBlenderExtraBotany3D(packsMap)` |
| [`L34593`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34593) | `Arche.Environment.hydrateBlenderAraratFlora3D(packsMap)` |
| [`L34960`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34960) | `Arche.Environment.hydrateBlenderBotany3D()` |
| [`L35225`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35225) | `Arche.Environment.hydrateMesopotamiaCityKit3D()` |
| [`L35835`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35835) | `Arche.Environment.updateCityLOD(cam, forceUpdate = false)` |
| [`L36004`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36004) | `Arche.Environment.hydrateShipyardIndustryKit3D()` |
| [`L36345`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36345) | `Arche.Environment.updateShipyardIndustryLOD(cam, forceUpdate = false)` |
| [`L36680`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36680) | `Arche.Environment.hydrateBlenderCharactersArarat3D()` |
| [`L36688`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36688) | `Arche.Environment.hydrateBlenderCharacters3D()` |
| [`L36990`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36990) | `Arche.Environment.updateCharactersLOD(cam, forceUpdate = false)` |
| [`L37072`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37072) | `Arche.Environment.updateWalkingCharactersLOD(cam, walkers, isDryCity)` |
| [`L37145`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37145) | `Arche.Environment.ensureAraratBuilt()` |
| [`L37161`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37161) | `Arche.Environment.buildAraratLandingSite3D()` |
| [`L39118`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39118) | `Arche.Environment.evalShipyardAbsTerrainZ(x, y)` |
| [`L39122`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39122) | `Arche.Environment.evalAraratAbsTerrainZ(x, y)` |
| [`L39127`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39127) | `Arche.Environment.evalTerrainBaseAbsNN(day)` |
| [`L39138`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39138) | `Arche.Environment.evalWaterLevelAbsNN(day)` |
| [`L39184`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39184) | `Arche.Environment.evalAbsoluteElevationCouple(wAbsNN, siteBaseNN, T_mean, hExtKeel)` |
| [`L39197`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39197) | `Arche.Environment.evalWaterRiseOffset(depth, T_mean, wAbsOverride, siteBaseOverride)` |
| [`L39205`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39205) | `Arche.Environment.updateLandmarksAndTerrain3D(depth, T_mean, dynHeaveZ, isThermalMode, isTexturedMode)` |
| [`L41033`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41033) | `Arche.Environment.updateFloatingMats3D(depth, waterRiseOffset, simTime, k, k_x, k_y, halfH, phi_rad, omega, wModel, mu_wind_rad, v_wind_ms, matsFrac, showWat)` |
| [`L50097`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L50097) | `Arche.Environment.updateHullWaterFilm3D(depth, dt_sim, isThermalMode)` |

### 5.3 Arche.Fauna (Organische Tiere, Ochsen & Knechte)

| Zeile | Funktion / Signatur |
|:-----:|:--------------------|
| [`L15962`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15962) | `Arche.Fauna.subdivideCatmullPts(pts, subdiv = 2)` |
| [`L15986`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15986) | `Arche.Fauna.buildOrganicLoftGeometry(tubes, radSegs = 20, subdiv = 2)` |
| [`L16053`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16053) | `Arche.Fauna.buildPbrMaps()` |
| [`L16116`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16116) | `Arche.Fauna.getMorphTypeForGenusId(genusId)` |
| [`L16135`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16135) | `Arche.Fauna.getFaunaBoardingHeaderGLSL(isDepthPass = false)` |
| [`L16326`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16326) | `Arche.Fauna._getArchetypeUniformValues(archetypeMode = 'QUAD')` |
| [`L16336`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16336) | `Arche.Fauna.getFaunaNormalDeformGLSL()` |
| [`L16402`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16402) | `Arche.Fauna.getFaunaVertexDeformGLSL(archetypeMode = 'QUAD', isDepthPass = false)` |
| [`L16904`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16904) | `Arche.Fauna.createFaunaDepthMaterial(archetypeMode = 'QUAD', locoScaleUniform = null, coatTypeId = 0.0)` |
| [`L16939`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16939) | `Arche.Fauna.createFaunaMaterial(rough = 0.62, baseHex = 0xffffff, coatClass = 'FUR', archetypeMode = 'QUAD', texOverrides = null)` |
| [`L17202`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17202) | `Arche.Fauna.createGroundImpactFX(parentGroup, maxPuffs = 64, maxRings = 56, isBasalt = false)` |
| [`L17364`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17364) | `Arche.Fauna.buildSculptedLimb(xHip, yHip, zHip, lenZ, rTop, rKnee, rHoof, cHide, isHind = false)` |
| [`L17378`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17378) | `Arche.Fauna.addHeadDetails(tubes, yEye, zEye, wHead, yEar, zEar, earW, earL, cIvory, hornType = 'BOVINE')` |
| [`L17430`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17430) | `Arche.Fauna.initArchetypesAndGoepelOxen()` |
| [`L17806`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17806) | `Arche.Fauna.getGenusInfo(genusId)` |
| [`L17841`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17841) | `Arche.Fauna.populateAllDecks()` |
| [`L18387`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18387) | `Arche.Fauna.resolveCollisionsAndClearCorridors()` |
| [`L18654`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18654) | `Arche.Fauna.syncVisibilityAndClip(zSliceMax)` |
| [`L18681`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18681) | `Arche.Fauna.updateShaderAndColors(ctx)` |
| [`L45208`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45208) | `Arche.Fauna.getIndividualHoverTooltip(ttKey, localPt, mode)` |

### 5.4 Arche.Physics (Wellen, Ozean, Mikroklima & Schichtpläne)

| Zeile | Funktion / Signatur |
|:-----:|:--------------------|
| [`L15580`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15580) | `Arche.Physics.evaluateGoepelShiftSchedule(timeOfDayHrs, isScheduleActive = false, overrideMode = null)` |
| [`L15612`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15612) | `Arche.Physics.evaluateArkTaxonomicCensus(payloadFrac = 1.0)` |
| [`L19250`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19250) | `Arche.Physics.evaluateShutterAerodynamics(headModeStr, v_roof_ms, rho_air, precip_mmh, isFullShipZohar = true, isBadgirActive = true, out = _shutterAeroScratch)` |
| [`L52362`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52362) | `Arche.Physics.evalWorldGroundSDF(wx, wy, wz)` |
| [`L52538`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52538) | `Arche.Physics.sampleMicroclimateAt(xShip, yShip, zShip, out = _microclimateScratch)` |
| [`L52624`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52624) | `Arche.Physics.evaluateAirflowVelocityField(xShip, yShip, zShip, out = _airflowVelScratch)` |

### 5.5 Arche.Performance & Quality-Governor

*Keine direkten Funktionsdeklarationen in dieser Sektion.*

### 5.6 Arche.UI & Bilinguale Tooltips

| Zeile | Funktion / Signatur |
|:-----:|:--------------------|
| [`L45340`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45340) | `Arche.UI.get3DHoverTooltipByMode(ttKey, localPt, overrideShaderMode = null)` |
| [`L45798`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45798) | `Arche.UI.getTooltip(key, lang = params.language, mode = Arche.State.viewShader, localPt = null)` |

### 5.7 Arche.Player & Kamera-Steuerung

| Zeile | Funktion / Signatur |
|:-----:|:--------------------|
| [`L52396`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52396) | `Arche.Player.flyTo(posArr, targetArr, durationSec = 1.25)` |
| [`L52411`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52411) | `Arche.Player.updateCameraAndLabels()` |

### 5.8 Top-Level Engine- & Lifecycle-Funktionen

| Zeile | Funktion / Signatur |
|:-----:|:--------------------|
| [`L2230`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2230) | `toggleBox(contentId, btnId)` |
| [`L2238`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2238) | `toggleMainTelemetryPanel()` |
| [`L2260`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2260) | `initMobileCamDpad()` |
| [`L2389`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2389) | `getDeckZ(kIdx, yVal)` |
| [`L2444`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2444) | `buildWoodMaterial(spec)` |
| [`L2509`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2509) | `getWoodMat(key)` |
| [`L2520`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2520) | `handsToM(val)` |
| [`L2523`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2523) | `handsToCm(val)` |
| [`L2526`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2526) | `toHandsVal(val)` |
| [`L2529`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2529) | `zoharSpacingToM(val)` |
| [`L2532`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2532) | `badgirHeightToM(val)` |
| [`L2535`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2535) | `isZoharFullShipExtent(modeStr)` |
| [`L2539`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2539) | `computeStructuralComponentMasses()` |
| [`L3204`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L3204) | `getDynamicDashboardTooltip(key)` |
| [`L4520`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L4520) | `getWoodTooltipHelper(propKey, labelDE, labelEN, roleDE, roleEN)` |
| [`L4542`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L4542) | `getDynamicGuiTooltip(ctrlKeyOrName)` |
| [`L5246`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5246) | `cpuNoise2D(x, y)` |
| [`L5326`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5326) | `fastNoise2D(x, y)` |
| [`L5339`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5339) | `generateAlbedo(typeId)` |
| [`L5430`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5430) | `generateNormal(normId)` |
| [`L5504`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5504) | `applyFinishedJob(res)` |
| [`L5543`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5543) | `triggerMainThreadFallback()` |
| [`L5548`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L5548) | `stepNextFallbackJob()` |
| [`L6699`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6699) | `orientCylinderUVsAlongAxis(geo, lengthM, radiusM)` |
| [`L6712`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6712) | `mergeTransformedGeos(entries)` |
| [`L6770`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6770) | `mergeRigidChildrenByMaterial(grp, excludeSet = null)` |
| [`L6822`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6822) | `createLanternPinionMesh(radius, length, nStaves, axis, diskMat, staveMat)` |
| [`L6851`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6851) | `createCrownWheelMesh(radius, rimThick, nTeeth, axis, toothSign, rimMat, toothMat)` |
| [`L6881`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6881) | `createArchimedeanHelixGeometry(rInner, rOuter, length, nTurns, radialSegs = 180)` |
| [`L6909`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6909) | `createWoodenDogClutchGroup(axis, hornbeamMat, oakMat)` |
| [`L8789`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8789) | `_computeTierAnisotropy(tierIdx)` |
| [`L8800`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8800) | `applyCleanTextureFiltering(tex, isColor)` |
| [`L8816`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8816) | `syncTextureAnisotropy(tierIdx)` |
| [`L8860`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8860) | `hasGLTFLoader()` |
| [`L8864`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8864) | `_getGLTFLoader(options)` |
| [`L8884`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8884) | `_isFileProtocol()` |
| [`L8888`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8888) | `_decodeBundleEntry(entry)` |
| [`L8908`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8908) | `_computeAssetModeColor(mat, viewShader, tEnv)` |
| [`L8924`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8924) | `attachArcheMaterialHooks(mat, options = {})` |
| [`L9201`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9201) | `syncViewShader(viewShader, tEnv)` |
| [`L9215`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9215) | `_parseGLTFBuffer(loader, arrayBuffer, resourcePath)` |
| [`L9230`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9230) | `_loadRawGLTFScene(slotKey, url, options = {})` |
| [`L9268`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9268) | `_applyTransformOpt(vec3Obj, val)` |
| [`L9275`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9275) | `_findManifestMeta(slotKey)` |
| [`L9290`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9290) | `loadGLBSlot(slotKey, url, targetParent, options = {})` |
| [`L9418`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9418) | `_isPlaceholderAlive(placeholder)` |
| [`L9428`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9428) | `_pruneStaleTargets(slotKey)` |
| [`L9442`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9442) | `_tryMountTarget(entry)` |
| [`L9527`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9527) | `registerReplaceTarget(slotKey, proceduralPlaceholderGroup, mountConfig = {})` |
| [`L9554`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9554) | `restoreProceduralFallback(slotKey)` |
| [`L9576`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9576) | `mountAllRegisteredSlots()` |
| [`L9589`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9589) | `initManifest(manifestUrl = 'assets/manifest.json')` |
| [`L9609`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9609) | `getStatus()` |
| [`L9628`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9628) | `extractInstancedTemplate(glbScene, options = {})` |
| [`L9687`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9687) | `createInstancedMesh(templateOrScene, maxCount, options = {})` |
| [`L9725`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9725) | `registerManagedMaterial(mat, options = {})` |
| [`L9748`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9748) | `configureSmoothLODGroup(lodGroup, opts = {})` |
| [`L11994`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L11994) | `createLayerBucket()` |
| [`L12013`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12013) | `woodKeyToTexIdx(woodKey)` |
| [`L12020`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12020) | `resolvePartDynamicTexIdx(bucket, x, y, z, nx, ny, nz, elemType, matType, fixTag, forceTexIdx)` |
| [`L12064`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12064) | `addQuadToBucket(bucket, p1, p2, p3, p1_dup, p3_dup, p4, nx, ny, nz, elemType, matType, fixTag = 0,...)` |
| [`L12114`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12114) | `refreshAllWoodMaterialGroups()` |
| [`L12153`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12153) | `addBoxToBucket(bucket, x0, x1, y0, y1, z0, z1, elemType, matType, fixTag = 0, forceTexIdx = -1)` |
| [`L12161`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12161) | `addThickQuadToBucket(bucket, p1, p2, p3, p4, dx, dy, dz, nx, ny, nz, elemType, matType, fixTag = 0)` |
| [`L12178`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12178) | `addStormShutterInstance(xShip, yShip, zHinge, spanW, chordH, sideDir, isBadgirFlap = false)` |
| [`L12190`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12190) | `addHorizontalBarrelCylinderRow(bucket, wireArr, x0, x1, yCenter, zCenter, radius, nSegs, fixTag = 3)` |
| [`L12196`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12196) | `addBoneTimberInstance(x0, y0, z0, x1, y1, z1, radius)` |
| [`L12207`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12207) | `addVolumetricBeddingZone(x0, x1, y0, y1, zBase, thicknessZ, moundPeakZ = 0.0, densityWeight = 1.0)` |
| [`L12217`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12217) | `buildVolumetricHullWallsAndDecks()` |
| [`L12241`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12241) | `addDeckBayWithCutout(x0, x1, y0, y1, z0, z1, cX0, cX1, cY0, cY1, matType, addGuardrail = false, openXSi...)` |
| [`L12848`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12848) | `addWireBox(x0, x1, y0, y1, z0, z1)` |
| [`L13089`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L13089) | `addBarrelPerpendicularToWallY(bucket, wireArr, xCenter, y0, y1, zCenter, radius, nSegs, fixTag = 3, cutawayHide ...)` |
| [`L13106`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L13106) | `addTransverseBulkheadBarrelRack(xR0, xR1, yRack0, yRack1, zKantTop, zDeck, rowCountsZ, forceColsY = 0)` |
| [`L13136`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L13136) | `addChineWallBarrelRack(xCh0, xCh1, yCh0, yCh1, zDeck, isPortSide, nColsX = 5, nRowsY = 2)` |
| [`L13196`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L13196) | `addDeck1MegafaunaStallRow(xM0, xM1, yBack, yFront, nStalls, skipWaveBSpec = false)` |
| [`L13286`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L13286) | `addFlushChuteSlottedOakGrating3D(xG0, xG1, yC0, yC1, zDeck)` |
| [`L13300`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L13300) | `addOpenFlushChute3D(x0, x1, y0, y1, zDeck)` |
| [`L13517`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L13517) | `addDeck2AnimalPenRow(xP0, xP1, yBack, yFront, nPens, hasMezz = true)` |
| [`L13729`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L13729) | `addDeck3AviaryBlock(xA0, xA1, y0, y1, nCages)` |
| [`L13818`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L13818) | `addDeck3RodentHoneycombBlock(xR0, xR1, yShelf, nCols, halfDepthY = 0.38)` |
| [`L14422`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L14422) | `buildGeometryMaterialGroups(geo, metaList, excludeWaveMask = 0)` |
| [`L14642`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L14642) | `pushBedShellQuad(p1, p2, p3, p4, u0, v0, u1, v1, hLay0, hLay1 = hLay0)` |
| [`L14899`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L14899) | `createGoepelWheelGroup(xCenter)` |
| [`L15403`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15403) | `createAnimatedPaternosterGroup(xCenter)` |
| [`L15541`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15541) | `updatePaternosterAnimation(pGroup, liftPhase)` |
| [`L15625`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15625) | `setDogClutchVisualState(clutchGrp, engaged)` |
| [`L15652`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15652) | `updateGoepelTransmissionKinematics(gMaster, deltaAngleRad, shiftState = null)` |
| [`L18801`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18801) | `writeSiloConeCell(cellIdx, x0, x1, y0, y1, zE00, zE10, zE11, zE01, xM, yM, zApex, rA, gA, bA, rE, gE...)` |
| [`L18826`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18826) | `writeTkWatQuad(qIdx, p1x, p1y, p1z, p2x, p2y, p2z, p3x, p3y, p3z, p4x, p4y, p4z, nx, ny, nz, rT, ...)` |
| [`L18854`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18854) | `updateSiloGrainAndHighTanks3D(H_silo_fill_m, d3TankFillFrac, d2SpuelFillFrac, rollRad, pitchRad, isThermalMode, ...)` |
| [`L18944`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18944) | `buildSloshingTankVolume(x0, x1, y0, y1, zBot, zMeanWat, rTop, gTop, bTop, rBot, gBot, bBot, phaseOff)` |
| [`L19059`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19059) | `writeBilgeQuad(qIdx, p1x, p1y, p1z, p2x, p2y, p2z, p3x, p3y, p3z, p4x, p4y, p4z, nx, ny, nz, rT, ...)` |
| [`L19079`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19079) | `getDoubleBottomChamberType(iSec, jBay)` |
| [`L19090`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19090) | `updateBilgeWater3D(h_bilge_eff, rollRad, pitchRad, isThermalMode, T_bilge_C, T_sea_C)` |
| [`L19198`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19198) | `pushShutterBox(x0, x1, y0, y1, z0, z1, uScale = 1.0, vScale = 1.0)` |
| [`L19477`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19477) | `updateLayerVisibilities()` |
| [`L19665`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19665) | `writeVolRestQuad(posArr, colArr, quadIdx, xA, yA, xB, yB, rTop, gTop, bTop, rBot, gBot, bBot)` |
| [`L19926`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19926) | `spawnSplashParticle(wx, wy, wz, vx, vy, vz, pSize = 1.6, lifeDur = 1.0, jitterXY = 1.6)` |
| [`L20090`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20090) | `updateGate3D(mode)` |
| [`L20224`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20224) | `_loadTexAsync(loader, url, isColor)` |
| [`L20240`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20240) | `_loadWoodLibraryTextures()` |
| [`L20260`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20260) | `_applyWoodSetToMat(mat, libKey)` |
| [`L20269`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20269) | `syncArkBaseWoodMaterials()` |
| [`L20284`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20284) | `_prepareArkGeometry(rawGeo, bakeZUp)` |
| [`L20296`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20296) | `_createArkStandardMaterial(srcMat, slotName)` |
| [`L20331`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20331) | `_collectLodGroupsFromScene(rawScene)` |
| [`L20357`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20357) | `rebuildArkCarpentryInstances()` |
| [`L20514`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20514) | `updateArkBadgirCaps(pairStations, zTop, isActiveTowers)` |
| [`L20542`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20542) | `syncArkWaveAVisibility(cullModeOverride)` |
| [`L20623`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20623) | `updateArkWaveALODs(cam, force)` |
| [`L20668`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20668) | `hydrateArkWaveAKits3D()` |
| [`L20946`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20946) | `_loadTexAsyncWB(loader, url, isColor)` |
| [`L20962`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20962) | `_prepGeoWB(rawGeo, bakeZUp = true)` |
| [`L20975`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20975) | `_collectWaveBNodes(sceneRoot)` |
| [`L21002`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21002) | `_ensureTrimMaterial(fallbackScene)` |
| [`L21042`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21042) | `_ensureHayStrawMaterial()` |
| [`L21080`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21080) | `_buildHeroLODGroup(lodMap, baseName, mat, ttKey)` |
| [`L21123`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21123) | `_buildInstancedFromNode(lodMap, baseName, matrices, mat, ttKey, parentGrp, preferLod = 0)` |
| [`L21144`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21144) | `_makeMatrix(px, py, pz, rx, ry, rz, sx, sy, sz)` |
| [`L21153`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21153) | `_preparePaternosterFrameGeo(rawGeo)` |
| [`L21181`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21181) | `syncArkWaveBBarrelsCount()` |
| [`L21227`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21227) | `syncArkWaveBVisibility(cullModeOverride)` |
| [`L21338`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21338) | `updateArkWaveBLODs(cam, force = false)` |
| [`L21373`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21373) | `syncArkWaveBMachineryInstances()` |
| [`L21411`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21411) | `hydrateArkWaveBKits3D()` |
| [`L22447`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22447) | `createGrassTuftGeo(h = 0.40, nBlades = 5, wBase = 0.12, wTop = 0.035)` |
| [`L22476`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22476) | `createShrubClusterGeo()` |
| [`L22520`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22520) | `createStaticGeometryBatcher()` |
| [`L22523`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22523) | `getBuffers(mat)` |
| [`L22532`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22532) | `addBox(mat, cx, cy, cz, sx, sy, sz, rx = 0, ry = 0, rz = 0)` |
| [`L22539`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22539) | `rotXform(x, y, z)` |
| [`L22549`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22549) | `rotNorm(nx, ny, nz)` |
| [`L22581`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22581) | `addStrut(mat, p0, p1, rTop, rBot, nSegs = 6)` |
| [`L22630`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22630) | `addCatenaryRope(mat, p0, p1, radius = 0.02, sagM = 0.14, nSteps = 12, nRadSegs = 6, windAmp = 0.035)` |
| [`L22727`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22727) | `addTentClothPanel(mat, cx, cy, cz, widthX, slopeL, rotX, nSegX = 12, nSegY = 6, rotZ = 0.0)` |
| [`L22735`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22735) | `evalPt(u, v)` |
| [`L22756`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22756) | `addGeometry(mat, srcGeo, matrix = null)` |
| [`L22784`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22784) | `buildMeshes(parentGroup, tooltipKey = null, opts = {})` |
| [`L22811`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22811) | `buildChunkedMeshes(parentGroup, tooltipKey = null, opts = {})` |
| [`L23217`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23217) | `calcNorm(px, py, pz)` |
| [`L25219`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25219) | `makeShipyardEnvMat(cacheKey, baseHex, rough, metal, fragExtraGLSL, options = {})` |
| [`L25899`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25899) | `nextRandC()` |
| [`L26655`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26655) | `nextRandVar()` |
| [`L27903`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27903) | `addAquaWater(geo, px, py, pz, rx = 0, quat = null)` |
| [`L28205`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28205) | `rotXY(cx, cy, lx, ly, yaw)` |
| [`L28209`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28209) | `addVillageSmoke(ox, oy, oz, pIdx)` |
| [`L28214`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28214) | `addMudbrickHouse(cx, cy, w, d, hWall, yaw, hasAwning, hasLadder, idx)` |
| [`L28624`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28624) | `addUrCourtyardHouse(cx, cy, w, d, h1, h2, yaw, awMat, hasOven, idx, targetBatch = cityBatch)` |
| [`L28658`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28658) | `addWingRoof(wx, wy, ww, wd, wh, addVigas)` |
| [`L28742`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28742) | `addUrInsula(cx, cy, totW, totD, cols, rows, yaw, seedOff, targetBatch = cityBatch)` |
| [`L28764`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28764) | `addUrCityGate(gx, gy, outYaw)` |
| [`L28832`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28832) | `addWallSpan(x0, y0, x1, y1, hWall, thick, hasCrenels = true, useKitWall = false)` |
| [`L29207`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29207) | `pushRoadTri(ax, ay, az, au, av, bx, by, bz, bu, bv, cx, cy, cz, cu, cv)` |
| [`L29211`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29211) | `addFlagstoneRoad(pts, width, tier = 0)` |
| [`L29288`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29288) | `pushStonePlazaPad(cxP, cyP, wP, dP, nxP = 4, nyP = 4, zLift = 0.042)` |
| [`L29326`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29326) | `pushOrgRoadTri(ax, ay, az, au, av, af, bx, by, bz, bu, bv, bf, cx, cy, cz, cu, cv, cf)` |
| [`L29331`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29331) | `addOrganicRoad(pts, width, meanderAmp = 0.55)` |
| [`L29754`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29754) | `appendCarvedCanalRibbon(pts, halfW, startExt = 0.0, endExt = 0.0, zStart = zCanalW, zEnd = zCanalW, watPts...)` |
| [`L29755`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29755) | `buildDensePath(srcPts)` |
| [`L30024`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30024) | `addRiverIntakeSluice(ix, iy, dirToLandX, zWat, spanHalf = 3.3)` |
| [`L30158`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30158) | `addMagurBoatSlot(hasLogs, x, y, z, yawZ, boatInfo)` |
| [`L30276`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30276) | `addCanalArchBridge(bx, by, yaw, spanW = 10.6, roadW = 4.2)` |
| [`L30293`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30293) | `addTimberJetty(jx, jy, yaw, len = 10.5, zWater = 0.80)` |
| [`L30311`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30311) | `addGrainSilo(sx, sy, rad = 2.35, h = 4.4)` |
| [`L30320`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30320) | `addMudhifHut(mx, my, yaw, len = 7.2, wid = 3.8)` |
| [`L30339`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30339) | `addTownKiln(kx, ky, smokeIdx)` |
| [`L30481`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30481) | `evalRegionalRoadDist(px, py)` |
| [`L30493`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30493) | `isSafeAgriSpot(wx, wy, minRoadDist = 5.0)` |
| [`L30585`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30585) | `addUprightStrawRick(fx, fy, fIdx, withThreshFloor)` |
| [`L30621`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30621) | `addFieldShelter(sx, sy, yaw)` |
| [`L30735`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30735) | `nextRandCrop()` |
| [`L31135`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31135) | `addCanalWeir(wx, wy, yaw, spanW = 6.4, zWater = 0.82)` |
| [`L31549`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31549) | `isInUrCityOrSuburb(x, y, pad = 0.0)` |
| [`L31557`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31557) | `isShipyardWorkZone(x, y, pad = 0.0, forTrees = false)` |
| [`L31905`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31905) | `nextRandG()` |
| [`L31975`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31975) | `nextRandS()` |
| [`L32190`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32190) | `nextRandSt()` |
| [`L32306`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32306) | `nextRandT()` |
| [`L33591`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33591) | `_loadSharedBotanyTextures()` |
| [`L33683`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33683) | `_prepTexForBotany(tex, isColor, repeatWrap)` |
| [`L33699`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33699) | `_adaptBotanyMaterial(species, srcMat, isFol, sharedTex, opts = {})` |
| [`L33778`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33778) | `_extractSpeciesPack(species, glbScene, sharedTex, opts = {})` |
| [`L34997`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34997) | `_createUnifiedWorldTrimMaterial(srcMat, opts = {})` |
| [`L35197`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35197) | `_createCityTrimMaterial(srcMat, isRoad = false)` |
| [`L35201`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35201) | `_openCityGateDoorsGeometry(geo)` |
| [`L36000`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36000) | `_createShipyardTrimMaterial(srcMat, isHot = false)` |
| [`L36498`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36498) | `_prepCharTex(tx, isColor)` |
| [`L36514`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36514) | `_loadLinearTex(url)` |
| [`L36522`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36522) | `_prepareCharacterGeo(obj, invRoot, rotX)` |
| [`L36566`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36566) | `_buildHeroLOD(figData, mat, tooltipKey, castShadowLod0 = true)` |
| [`L36588`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36588) | `_pickCitizenTypeForDryWorker(wp, idx)` |
| [`L36609`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36609) | `_pickCitizenTypeForWalker(cw, idx)` |
| [`L36631`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36631) | `_mountAraratCharactersFromCache()` |
| [`L38802`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38802) | `nextRandSp()` |
| [`L38878`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38878) | `nextRandSap()` |
| [`L41237`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41237) | `getDeviceClass()` |
| [`L41249`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41249) | `detectInitialTier()` |
| [`L41281`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41281) | `resolveTierFromMode(pMode)` |
| [`L41291`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41291) | `applyTier(tierIdx, force = false)` |
| [`L41366`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41366) | `resetGovernorClock()` |
| [`L41375`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41375) | `tickGovernor(nowMs)` |
| [`L41442`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41442) | `getCurrentSpec()` |
| [`L41446`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41446) | `setProfileMode(modeStr)` |
| [`L41458`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41458) | `init()` |
| [`L41466`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41466) | `restoreStandardVisibilities()` |
| [`L41512`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41512) | `updateExteriorPortalCulling(cam)` |
| [`L41668`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41668) | `updateLegendMode(mode)` |
| [`L41811`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41811) | `updateScenarioDescription(scenName)` |
| [`L42120`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42120) | `translateGUI(lang)` |
| [`L42151`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42151) | `translateDOM(lang)` |
| [`L42379`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42379) | `showExpeditionBriefing()` |
| [`L42386`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42386) | `hideExpeditionBriefing()` |
| [`L42393`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42393) | `selectAppModeAndStart(mode)` |
| [`L42457`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42457) | `toggleLabExpeditionMode()` |
| [`L42466`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42466) | `reopenOnboardingModal(directBriefing = false)` |
| [`L42473`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42473) | `toggleLanguage(forceLang)` |
| [`L42681`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42681) | `getBadgirPairStationsX(count)` |
| [`L42689`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42689) | `updateBucketMeshGeometry(bucket)` |
| [`L42723`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42723) | `addPath(fn, pathType)` |
| [`L42745`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42745) | `bezier3(p0, p1, p2, p3, u)` |
| [`L43082`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43082) | `updateZoharAndBadgirGeometry()` |
| [`L43337`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43337) | `computeBadgirMassTons()` |
| [`L43370`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43370) | `resetWaveAndShipState()` |
| [`L43626`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43626) | `triggerPauseEquilibriumRelax()` |
| [`L43630`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43630) | `markCustomPreset()` |
| [`L43687`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43687) | `syncQuickViewDock()` |
| [`L43703`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43703) | `toggleQuickAirflow()` |
| [`L43709`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43709) | `setQuickShader(modeStr)` |
| [`L43715`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43715) | `setQuickSlice(sliceStr)` |
| [`L43721`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43721) | `setQuickWall(wallStr)` |
| [`L43755`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43755) | `enterArkInterior()` |
| [`L43772`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43772) | `flyToInteriorDeck(deckKey)` |
| [`L43799`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43799) | `updateInteriorNavHUD(forceNow = false)` |
| [`L44017`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44017) | `toggleHighlightTour()` |
| [`L44022`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44022) | `toggleFreeCameraMode(forceVal)` |
| [`L44207`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44207) | `applyPiersonMoskowitzWindSea(v_kmh)` |
| [`L44280`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44280) | `evaluateExpeditionLogistics(day, rain_mmh = 0.0, T_stall_C = 20.8, depth_m = 0.0, woodMoisturePct = 13.5, out ...)` |
| [`L44407`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44407) | `evaluateBiblicalChronicleState(day, instantSnap = false)` |
| [`L44808`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44808) | `syncChronicleUI()` |
| [`L44893`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44893) | `toggleChronicleVoyage()` |
| [`L44911`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44911) | `startPreFloodBunkering()` |
| [`L44926`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44926) | `resetVoyageToLand()` |
| [`L44940`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44940) | `changeChronicleSpeed(val)` |
| [`L44945`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44945) | `scrubChronicleDay(val)` |
| [`L44988`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44988) | `computeRawICDNodeKN(wallIdx, lvlIdx, stIdx)` |
| [`L45034`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45034) | `computeScaledICDNodeKN(wallIdx, lvlIdx, stIdx, precomputedRawSum = null)` |
| [`L45050`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45050) | `generateICDMarkdownReport()` |
| [`L45128`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45128) | `translateMarkdownReportEN(md)` |
| [`L45148`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45148) | `openICDModal()` |
| [`L45161`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45161) | `refreshICDMarkdown()` |
| [`L45169`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45169) | `closeICDModal()` |
| [`L45172`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45172) | `copyICDMarkdown()` |
| [`L45182`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45182) | `downloadICDMarkdown()` |
| [`L45195`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45195) | `getFixturePopularTooltip(key)` |
| [`L45810`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45810) | `renderActiveTooltipContent()` |
| [`L45827`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45827) | `showDynamicTooltip(source, key, clientX, clientY)` |
| [`L45837`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45837) | `positionSciTooltip(clientX, clientY)` |
| [`L45851`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45851) | `hideSciTooltip()` |
| [`L45883`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45883) | `resolve3DFixtureTooltipKey(hitObj, localPt, instanceId = undefined)` |
| [`L46050`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46050) | `_syncHoverSkipSet()` |
| [`L46109`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46109) | `_collectHoverTargets(node, out)` |
| [`L46129`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46129) | `_raycastInstancedFast(obj, worldRay, bestLimitDist)` |
| [`L46184`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46184) | `_precomputeHoverBounds()` |
| [`L46203`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46203) | `perform3DRaycastInspect(clientX, clientY)` |
| [`L46446`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46446) | `computeUtilizationRGB(etaEC5, etaBruch, blinkState, outRGB)` |
| [`L46489`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46489) | `computeThermalRGB(tempC, outRGB)` |
| [`L46518`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46518) | `getBeaufortInfo(v_kmh)` |
| [`L46533`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46533) | `update3DLabel(mesh, domElem)` |
| [`L46546`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46546) | `getBarColor(etaEC5, etaBruch)` |
| [`L46553`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46553) | `computeHullSectionProperties(hasCrossBracing, hasHeavyPlanking, hasSwelling, tempInteriorC, effWaveHalfLen_m)` |
| [`L46708`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46708) | `evalWebES(z_upper)` |
| [`L46757`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46757) | `evalESRatio(z_val)` |
| [`L46818`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46818) | `evaluateOceanWave(x_ship, y_ship, k, k_x, k_y, halfH, phi_rad, omega, depth, waveModel, out)` |
| [`L46873`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46873) | `getStationEffectiveKNPerMeter(stIdx)` |
| [`L46894`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46894) | `evaluateICDWeightPerMeterMN(xs, totalWeightMN, payloadFrac)` |
| [`L46904`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46904) | `writeVolumeQuad(posArr, colArr, quadIdx, xA, yA, zTopA, rA, gA, bA, xB, yB, zTopB, rB, gB, bB, zFl...)` |
| [`L46919`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46919) | `writeFilmQuad(posArr, normArr, colArr, quadIdx, x0, y0, zBot0, zTop0, x1, y1, zBot1, zTop1, nx, ...)` |
| [`L46939`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46939) | `initOceanWaveWorker()` |
| [`L46945`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46945) | `evaluateExactHydrostatics(M_akt_t, V_ext_keels_m3, h_ext_keel_m, out = _maritimeScratch, rho_sea_override = ...)` |
| [`L46964`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46964) | `evaluateTransverseWaveFKFactor(k_y, B = B_SHIP)` |
| [`L46971`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46971) | `evaluateStripAddedMassAndSlam(subDraft, depth, geomSubDraft, draftBB_clean, draftSB_clean, vUpMid, vUpBB, vUpSB,...)` |
| [`L47002`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47002) | `stepSemiImplicitHeavePitch(heaveZ, heaveVel, heaveAcc, M11, C11, K11, pitchRad, pitchVel, pitchAcc, M22, C22,...)` |
| [`L47028`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47028) | `evaluateMetabolicHeatResponse(T_stall_C)` |
| [`L47038`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47038) | `evaluateBarnPhysiologyAndGasBalance(T_mean_C, RH_pct, T_bilge_C, Q_solar_roof_kW, Q_bio_total_kW, steamRate_kgh, V_dot...)` |
| [`L47145`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47145) | `evaluateAstronomyAndPsychrometrics(timeOfDay, latitude, cloudCover, extHumidity, precipIntensity, tAir, tWater, airPr...)` |
| [`L47260`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47260) | `evaluateCharnockWindAndSolAir(v_wind_10_kmh, H_wave, T_mean, badgirHeight, mu_wind_rad, rho_air, M_akt_t, GM_tra...)` |
| [`L47352`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47352) | `evaluateMassAndStabilityBalance(payloadPct, precipIntensity, dynRollRad, oxenBioEff, timeOfDay, out = _massStabScr...)` |
| [`L47535`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47535) | `evaluateThermalNetworkAndVentilation(T_current_C, prevRelHumidity, P_goepel_W, payloadFrac, waterDepth_m, T_mean, freeb...)` |
| [`L47655`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47655) | `evalStallHeatBalanceResidual(T_cand)` |
| [`L47897`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47897) | `evaluateDAlembertStripDynamics(k, k_x, k_y, halfH, phi_rad, omega, depth, wModel, mu_rad, T_mean, KG_height, M_ak...)` |
| [`L48184`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48184) | `evaluateRollAndSurgeSwayDynamics(dynamicMotion, autoPlay, dt_phys, halfH, depth, T_mean, BM_radius, KG_height, GM_t...)` |
| [`L48382`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48382) | `evaluateSideGateHydrostatics(gateMode, isSideGateOpen, zWaterAtGate, T_mean, dynHeaveZ, dynPitchRad, dynRollRad...)` |
| [`L48508`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48508) | `evaluateInternalFixturesMechanics(payloadFrac, oxenPresence, oxenBioEfficiency, H_wave, dynRollRad, dynPitchRad, dyn...)` |
| [`L48523`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48523) | `evalLocalG(x_m, y_m)` |
| [`L49003`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49003) | `evaluateHullHotspotsAndLUTs(payloadFrac, M_nutz_akt, m_roof_dyn, M_rain_roof_t, M_rain_soak_t, h_bilge_eff_m, ...)` |
| [`L49295`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49295) | `evaluateFatigueAndHotspotEC5(fatigueEnabled, chronicleActive, autoPlay, dt_phys, eqHoursStep, H_wave, omega, ma...)` |
| [`L49442`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49442) | `evaluate3DFieldPointMechanicsAndThermal(meta, isBadgirPart, isRoofPart, ctx = _shaderFrameCtx, out = _fieldPointScratch)` |
| [`L49909`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49909) | `evaluateVertexBufferColors(metaList, targetColArr, isBadgirPart, isRoofPart = false, ctx = _shaderFrameCtx)` |
| [`L50010`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L50010) | `evaluateEC5AndNorris(sigma_glob, sigma_loc_bend, sigma_90_trans, tau_xy, matObj, isScarfLoc, d_member_m...)` |
| [`L50604`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L50604) | `_initSSCS()` |
| [`L50769`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L50769) | `_resizeSSCS()` |
| [`L50781`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L50781) | `_isSSCSNearScene()` |
| [`L50801`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L50801) | `_runSSCSContactPass()` |
| [`L50993`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L50993) | `_compositeSSCSContactPass()` |
| [`L51003`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L51003) | `animate(isSingleTestStep = false)` |
| [`L52466`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52466) | `syncMobileViewportAndPerf(isInit = false)` |
| [`L52728`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52728) | `runArcheUnitTests()` |
| [`L52737`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52737) | `assertTest(suite, name, condition, detailStr)` |
| [`L54051`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L54051) | `openUnitTestModal(e)` |
| [`L54183`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L54183) | `_setBootProgressUI(pct, stageIdx, textDE, textEN)` |
| [`L54202`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L54202) | `_nextFrameYield()` |
| [`L54209`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L54209) | `_withTimeout(promise, ms, fallbackVal = false)` |
| [`L54222`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L54222) | `_computeMaterialProgramSig(obj, mat)` |
| [`L54250`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L54250) | `prewarmSimulationShaders(onProgress)` |
| [`L54624`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L54624) | `startArcheSimulationCleanly()` |


---

## 6. Vollständiges Unit-Test-Kataster (T01 bis T101)

> Ausgeführt durch `runArcheUnitTests()` (ab Zeile ~27436).  
> **Gesamt: 101 Tests** — 100% abgedeckt.

| ID | Zeile | Test-Suite | Test-Bezeichnung |
|:--:|:-----:|:-----------|:-----------------|
| **T01** | [`L52773`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52773) | 1. Ellen-Kanon, EN 338 & Clean Architecture | Biblische Hauptabmessungen (300 × 50 × 30 Ellen) |
| **T02** | [`L52778`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52778) | 1. Ellen-Kanon, EN 338 & Clean Architecture | 6–5–4–3-Handbreiten-Normquerschnitte (Glatte Handbreiten ohne cm-Rundung) |
| **T03** | [`L52783`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52783) | 1. Ellen-Kanon, EN 338 & Clean Architecture | EN 338 Fraktilmodul E_0,05 (Laubholz 0.84 vs. Nadelholz 0.67) |
| **T04** | [`L52789`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52789) | 1. Ellen-Kanon, EN 338 & Clean Architecture | EC5 Bemessungswerte f_d = f_k * k_mod / γ_M (NKL 3) |
| **T05** | [`L52793`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52793) | 1. Ellen-Kanon, EN 338 & Clean Architecture | 300-Knoten-ICD-Kataster Vollständigkeit & Symmetrie |
| **T06** | [`L52803`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52803) | 1. Ellen-Kanon, EN 338 & Clean Architecture | Glatte Ellen- & Handbreiten-Konsistenz (0,000 mm Zentimeter-Rundungsabweichung) |
| **T07** | [`L52814`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52814) | 1. Ellen-Kanon, EN 338 & Clean Architecture | Clean-Architecture-Registry (Arche.Groups & Arche.Materials), Basalt-Kombüse S7, Svalbard-Zeer & 0-ms-Schnittebene |
| **T08** | [`L52824`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52824) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Archimedisches Gleichgewicht T = (V_disp - V_Kiele) / (L*B*C_B) |
| **T09** | [`L52831`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52831) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Volumetrische Sensitivität V × ρ_EN338 (Sohle 5,0 Hände -> 6,5 Hände) |
| **T10** | [`L52835`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52835) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Metazentrische Anfangsstabilität GM_eff > 4.0 m |
| **T11** | [`L52839`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52839) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Freie-Oberflächen-Unterdrückung durch 7.500 Einzelfässer |
| **T12** | [`L52843`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52843) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | 3 Äußere Eichenkiele (Strandungs-Aufstandsfläche ≥ 350 m²) |
| **T13** | [`L52849`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52849) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Exakter Steiner-Formschwerpunkt KB & BM inkl. 3 Außenkiele |
| **T14** | [`L52861`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52861) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | D1-Fass-Wechselballast senkt KG, erhöht Tiefgang T & aufrichtendes Moment M·GM |
| **T15** | [`L52868`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52868) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Manning-Strickler-Regenwasseraufstau & Bilgenzulauf bei 1.200 mm/h Monsun |
| **T16** | [`L52874`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52874) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Kreiszylinder-Sehnenbreite b(h) = 2·√(R²-(h-R)²) maximiert |ΔGM| bei 50% Füllung |
| **T17** | [`L52880`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52880) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Flacher Bilgensumpf Pocket-Effekt dämpft freie Oberfläche bei starker Krängung |
| **T18** | [`L52901`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52901) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | 3D-Fass-Inventur (7.920 echte 8-Hände-Fässer) & 0 % Kollision (Silos, Schotttüren S1/14, Bâdgir-Schächte & Schnecken S4/11) |
| **T19** | [`L52910`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52910) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Miche-Flachwasser-Brecherlimit (H=20m bei d=12m begrenzt) |
| **T20** | [`L52917`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52917) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Stokes 3. Ordnung Kamm-Aufsteilung (η_Stokes > η_Sinus bei θ=0) |
| **T21** | [`L52923`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52923) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Wendel/Kim-Flachwasser-Quetschströmung (m'_add,flach > m'_add,tief) |
| **T22** | [`L52929`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52929) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Wagner/Ochi-Motter Keilslamming (Deadrise-Dämpfung bei φ=10° Krängung) |
| **T23** | [`L52935`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52935) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Analytischer Quer-Beugungsfaktor κ_trans(k_y*B) in Lang- vs. Kurzwelle |
| **T24** | [`L52941`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52941) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Unbedingte Stabilität des semi-impliziten Winkler-Felskontakt-Integrators |
| **T25** | [`L52948`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52948) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Nichtlineare Wall-Sided-Stabilität GZ(φ) > GM·sin(φ) bei φ = 15° |
| **T26** | [`L52959`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52959) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Ikeda-Kimmwirbeldämpfung B44_ikeda (Mittelkiel Y=0 + 2 Kimmkiele Y=±17.5 E.) |
| **T27** | [`L52963`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52963) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Vollständiger 6-DOF Roll-Trägheitstensor I_xx,tot (Struktur + ICD-Ladung + Added Mass) |
| **T28** | [`L52971`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52971) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | 2D-Beugungs-Surge (Auslöschung sinc(k_x·L/2) = 0 bei λ = L = 140 m vs. Langwelle) |
| **T29** | [`L52976`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52976) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Bodenkontakt-Arretierung (groundLock = 0 sperrt Surge/Sway bei Strandung) |
| **T30** | [`L52980`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52980) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Exakte Einzelpositionen (15 Längsgurte, 45 Stützen & 8 Bâdgire @ Y=±4.18m) in I_xx |
| **T31** | [`L52991`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52991) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Exakter Querkraft-Abschluss V_z(0) = 0 & V_z(140m) = 0 MN |
| **T32** | [`L52995`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52995) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Exakter Biegemoment-Abschluss M_y(0) = 0 & M_y(140m) = 0 MNm |
| **T33** | [`L52999`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52999) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Elastische 2-Knoten-Whipping-Eigenfrequenz f_1 im Zielband |
| **T34** | [`L53005`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53005) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | EC5 Anhang B (Möhler) — Wurzelknie erhöhen γ_mean & I_y,eff |
| **T35** | [`L53013`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53013) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | EC5 Gl. (6.17) — Exakt 100.0% bei σ_t,0,d = η_Schäft * f_t,0,d |
| **T36** | [`L53022`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53022) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | EC5 Gl. (6.19) — Quadratische Druck-Biege-Interaktion (u_c² + u_m) |
| **T37** | [`L53028`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53028) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | EC5 Gl. (6.23) — Biegeknicken (λ_rel > 0.30 -> k_c < 1.0 erhöht Ausnutzung) |
| **T38** | [`L53034`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53034) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | EC5 Gl. (3.1) — Höhenbeiwert k_h = (150/h)^0.2 für h < 150 mm |
| **T39** | [`L53040`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53040) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | 2D-Norris — Biaxiale Zug-Querdruck-Verschärfung (-u_0*u_90 > 0) |
| **T40** | [`L53044`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53044) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Johansen-Dübeltragfähigkeit (EC5 Gl. 8.6 & B.10) & Gustafsson k_v |
| **T41** | [`L53051`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53051) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Headless 2×2-D'Alembert-Löser schließt V_z(L), M_y(L) & M_t(L) exakt auf Null |
| **T42** | [`L53059`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53059) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | 3-Kiele-Winkler-Bodenkontakt erzeugt aufrichtendes Rollmoment (Y = ±17.5 E.) |
| **T43** | [`L53068`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53068) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Biaxiale Schrägbiegung (M_z), Vlasov-Wölbkrafttorsion & Racking-Schub in der 15×4-Hotspot-Suche |
| **T44** | [`L53079`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53079) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | 300-Knoten-Querdruck-LUT — 45 Eichen-Königsstützen senken Schwellen-Querdruck |σ_c,90| um >30% |
| **T45** | [`L53085`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53085) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | EC5 Gl. (6.15) Schub-Torsions-Interaktion, Gl. (B.10) Johansen-Dübel & Strandungspressung p_Strand |
| **T46** | [`L53097`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53097) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Kimmkanten-Rahmeneinspannung (L-Wurzelknie leiten Sohlenmoment in untere Bordwand ein) |
| **T47** | [`L53110`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53110) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Vierendeel-Rahmenbiegung & Eichen-Blockzargen-Entlastung an den 201 Schotttüren |
| **T48** | [`L53118`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53118) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | 2D-Zwischendeck-Durchlaufträgerbiegung σ_m = q·l²/(10·W) skaliert mit ICD-Knotenlast |
| **T49** | [`L53129`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53129) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Zohar-Ellen-Ausdehnung (300×50 E. vs. 260×21,5 E.) koppelt konsistent in Dachmasse & Vlasov-Torsion |
| **T50** | [`L53141`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53141) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Geschlossener Waben-Schott-Silo (I_y,Möhler > 400 m⁴, 0 Türen in S3/6/9/12 & 4:1 Schott-Widerstandsmoment) |
| **T51** | [`L53151`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53151) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | 720 Eichen-Wurzelknie (fixTag=5: Kimm-Wasserdruck nur außen, Norm-EC5 < 65% & Bruch-Stopp-Kopplung aktiv) |
| **T52** | [`L53160`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53160) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Hydrostatische Querquetschung (Querschott-Knicken), Dübel-Wechsellast-Verschleiß (K_ser) & Feuchte-Schüsselung (σ_cup,90) |
| **T53** | [`L53200`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53200) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Gen 8,1 Großer Gott-Wind (175 km/h Orkan, H=11,8m, 55° Schrägsee) — Innenschotten bruchsicher über 360° Phase |
| **T54** | [`L53245`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53245) | 5. 371-Tage-Chronik, Ermüdung & Instandhaltung | 371-Tage-Chronik (Kap. 14/15: Tag -20 leer -> Tag 20 Monsun -> Tag 146,5 Gott-Wind -> Tag 150 Grundsitz -> Tag 298 Ovoli -> Tag 371) |
| **T55** | [`L53250`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53250) | 5. 371-Tage-Chronik, Ermüdung & Instandhaltung | Palmgren-Miner-Wöhler-Akkumulation & logarithmische Madison-Dauerstandkurve k_mod(t) |
| **T56** | [`L53255`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53255) | 5. 371-Tage-Chronik, Ermüdung & Instandhaltung | Besatzungs-Wartung (Nachkeilen der 80.000 Hartholzdübel & Nachpechen in ruhiger Dünung) |
| **T57** | [`L53263`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53263) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Janssen-Silomechanik — Exakte Massenerhaltung (Wand + Sattel = 2.200 t) |
| **T58** | [`L53267`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53267) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Euler-Eytelwein-Seiltrieb (Paternoster F_Last > F_Leer, Ausnutzung < 100%) |
| **T59** | [`L53271`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53271) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | 3-Bahnen-Verteiler-Hub — Großtier-Rampen-Trittsicherheit S_Tritt > 1.50 |
| **T60** | [`L53275`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53275) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Alle 14 Einbauten-Systeme frei von NaN & im EC5-Bemessungsrahmen |
| **T61** | [`L53281`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53281) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | 9×8-Ellen-Seitentor Hydrostatik (F_w = ρ·g·A_w·h_c) & 6-Hände-Blockzargen-Schutz |
| **T62** | [`L53286`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53286) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Torricelli-Flutungs-Hydraulik Q_flood bei offenem 9×8-Ellen-Seitentor (4,0 Hände Bordwand) |
| **T63** | [`L53291`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53291) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Ortsaufgelöste Janssen-Silodruck-Erhöhung (Außenblöcke S3/S12 |Δx|=45m > Innen S6/S9 |Δx|=15m) |
| **T64** | [`L53295`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53295) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Vor-/Achterschiff-Asymmetrie der beiden Paternoster & Göpel (S4 @ X=35m vs. S11 @ X=105m) |
| **T65** | [`L53300`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53300) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Großtier-Rampen-Trittsicherheit S_Tritt(θ,φ) & 5,4-t-Basalt-Kombüsen (max g_eff S7/S13) |
| **T66** | [`L53310`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53310) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | 3D-Janssen-Tiefenprofil in den 224 Silowänden & 60°-Trichtersattel (Sattel > Fuß > Kopf) |
| **T67** | [`L53323`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53323) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Holz-Stein-Tribologie (6:1 Stockgetriebe im Ellen-Maß) & 12,3-kWh-Schichtfahrplan (5,5 h/Tag, Kap. 9.4–9.5) |
| **T68** | [`L53339`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53339) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | 3-Zweig-Kupplungsgetriebe (Exakte Drehmoment-Bilanz ΣM_Zweige = M_Göpel & Lastabwurf beim Auskuppeln) |
| **T69** | [`L53344`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53344) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Saint-Venant-Wellentorsion τ_t = 16·M_t/(π·D³) (Königswelle D=6H vs. 6:1-Querwellen D=2H) |
| **T70** | [`L53349`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53349) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Synchronisierte Deck-3-Einbauten (Basalt-Kombüse S7, Svalbard-Zeer S8 & Zimmermannswerkstatt |WERK|) |
| **T71** | [`L53357`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53357) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | 3D-Kraftfluss-Overlay (6 Zugkraft-Vektoren, 4 Drehmoment-Stromlinien & 3D-Schneckenwasserstrom) |
| **T72** | [`L53364`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53364) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Psychrometrie & Svalbard-Kühlung (T_FK <= T_Saatgut <= T_Stall) |
| **T73** | [`L53368`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53368) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Rinder-Physiologie (Boviner THI < 72 & DIN 18910 CO₂ < 3.000 ppm im Normfall) |
| **T74** | [`L53375`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53375) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | CIGR-Thermogenese (<8°C) vs. NRC-Anorexie-Drosselung (>26°C) |
| **T75** | [`L53381`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53381) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Ammoniak-Urease (NH₃ < 20 ppm) & Seewasser-Schwallspülung + CH₄-UEG |
| **T76** | [`L53385`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53385) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Vertikale 3-Decks-Temperaturschichtung (T_D1 < T_D2 < T_D3) |
| **T77** | [`L53390`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53390) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Bovine Kerntemperatur T_core (Hyperthermie bei Hitzestau) & Trinkwasserbedarf |
| **T78** | [`L53396`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53396) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | DIN-18910-Schadgas-Anstieg bei geschlossenen Schotttüren & Schwachlüftung |
| **T79** | [`L53402`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53402) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Sonnenbahn (Mittagszenit α = 90° - |φ - δ| = 68° vs. Mitternacht α < 0°) |
| **T80** | [`L53408`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53408) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Dalton-Gasgesetz & Magnus-Taupunkt (Feuchte Luft ist leichter als trockene Luft!) |
| **T81** | [`L53414`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53414) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Charnock-Meeresrauigkeit z_0 & logarithmisches Prandtl-Windprofil v_First > v_10 > v_Mid |
| **T82** | [`L53420`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53420) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Sol-Air-Dachbilanz — Solar-Aufheizung am Tag vs. Stefan-Boltzmann-Unterkühlung nachts |
| **T83** | [`L53425`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53425) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Psychrometrische Monsun-Dachkühlung (T_sol-air nähert sich bei Starkregen T_precip an) |
| **T84** | [`L53434`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53434) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Borda-Carnot-Schotttüren — Geschlossene Türen drosseln Lüftung & heizen Stall auf |
| **T85** | [`L53440`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53440) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | 14-Schritt-Bisektion & 2. Hauptsatz im Bilgen-Wärmetauscher (12°C vs. 34°C Meer) |
| **T86** | [`L53451`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53451) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Bâdgir-Innenschächte verhindern Dach-Kurzschluss & senken Turmfuß-Biegung um >60% |
| **T87** | [`L53464`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53464) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | 3D-Infrarot-Thermografie (T_Unterwasserwand < T_Innenstall < T_Sol-Air-Dach) |
| **T88** | [`L53473`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53473) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Bewegliche 3D-Sturmklappen an Zohar & Bâdgiren (Luv/Lee-Automatik im 1-Draw-Call InstancedMesh) |
| **T89** | [`L53480`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53480) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Dynamische Sturmklappen-Aerodynamik (α_Luv schließt im Orkan -> c_w sinkt & 94% Schlagregen-Abweisung) |
| **T90** | [`L53488`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53488) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | O2-Bilanz (RQ=0.85), H2S-Sulfat-Faulgas (Pumpen EIN vs. AUS), Erdregister & Silo-Taupunktschutz (> +3 K) |
| **T91** | [`L53504`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53504) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Manuelle Steuerung von Regentemperatur (T_Regen) & Bilgenwassertemperatur (T_Bilge) im Wärmenetzwerk |
| **T92** | [`L53529`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53529) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Wetter-Pakete A–D, 14 Szenario-Presets & 3D-Mikroklima-API (EC1-Schneelast, 3000m Ararat, ρ_See, Kombüse vs. Svalbard) |
| **T93** | [`L53541`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53541) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | Tierbestand (2.800 Gattungen | 6.350 Tiere | 1.100 t) & 3-m³-Svalbard-Tresor (40 Pithoi + 12 Zeer-Kühlröhren, Kap. 12.5) |
| **T94** | [`L53570`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53570) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | 3D-Fauna-Engine (6.350 Tiere, 8 Groß-Volieren vor Silos, Bâdgir-Öffnungen D1–D3 & Rinnen nur im Hauptgang) |
| **T95** | [`L53607`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53607) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | Zweisprachige DE/EN-Tooltip-Engine (100% Abdeckung für alle Dashboard-Keys, 67 GUI-Regler & 15 Szenarien) |
| **T96** | [`L53630`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53630) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | Modus-sensitiver 3D-Hover (Museum=Funktion | EC5=Kraft & % | Thermo=°C) & Auto-Gerätesprache (DE/EN) |
| **T97** | [`L53641`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53641) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | Numerische Stabilität — 0 NaN/Infinity-Werte im gesamten liveState |
| **T98** | [`L53702`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53702) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | 3D-Luftstrom-Netz (Arche.Groups.airflow3D ≥ 1500 Vertices), Zweikammer-Geschwindigkeitsfeld (Bâdgir Fall/Kamin, Atrium, Silo), CH4-Schichtung & Windwinkel-Kopplung (μ=90° > μ=0°) |
| **T99** | [`L53722`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53722) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | macOS Safari/Metal-GLSL-Konformität, Auto-FPS-Governor (≥ 30 FPS) & Mobile-UX |
| **T100** | [`L53804`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53804) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | Vollständige GPU-Beschleunigung (GPU-Stokes-Ozean, Ballistischer GPU-Splash-Shader & 0-ms-GPU-Instanz-Clipping) |
| **T101** | [`L54020`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L54020) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | Bronzezeitlicher Werftplatz (Tag -7) & Ararat-Hochgebirgsmassiv (Tag 150–371) |

---
*Ende des generierten Index. Bei jeder Code-Modifikation `node index_arche.js` im Terminal ausführen!*
