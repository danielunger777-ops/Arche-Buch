# ARCHE STRUKTUR-INDEX (`ARCHE_INDEX.md`)

> **Automatisch generiert durch `node index_arche.js`**  
> **Hauptdatei:** [`Arche Simulation 3.0.html`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html)  
> **Umfang:** **54.898 Zeilen** | **3200.2 KB**  
> **Stand:** 21.11.2026, 18:01:48

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
| [`L54895`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L54895) | `</script>` | Ende Haupt-JavaScript |
| [`L54896`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L54896) | `</body>` | Ende DOM-Hierarchie |

---

## 2. Arche Namespaces & Kern-Registries

| Zeile | Namespace | Beschreibung |
|:-----:|:----------|:-------------|
| [`L2052`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2052) | `window.Arche` | Arche Root-Namespace & State/Config/Kinematik-Arrays |
| [`L2224`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L2224) | `Arche.UI` | UI-DOM-Bindings, Bilinguale Tooltips (DE/EN) & Viewport-Sync |
| [`L3127`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L3127) | `Arche.I18n` | Bilinguale Sprach-Engine (DE/EN), GUI-Labels & Option-Maps |
| [`L6960`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6960) | `Arche.Groups` | Three.js Szenengruppen-Registry (hullGroup, interiorGroup, shipyardGroup, etc.) |
| [`L8750`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8750) | `Arche.Materials` | Material-Registry (Gopherholz, Eiche, Zypresse, Bronze, Wasser, etc.) |
| [`L41211`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41211) | `Arche.Performance` | Auto-FPS-Governor (Tier 1-4 Quality-Manager) & Instanz-Reduktion |

---

## 3. Architektur-Meilensteine & Baugruppen-Banner

| Zeile | Abschnitt / Banner-Titel |
|:-----:|:-------------------------|
| [`L8787`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8787) | **BLENDER -> ARCHE .GLB-ASSET-PIPELINE (Arche.Assets)** |
| [`L18395`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18395) | **ANALYTISCHER 3D-KOLLISIONS-, FASS- & GANG-FREIHALTE-SOLVER (PBD, 14 ITER.)** |
| [`L20155`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20155) | **1B. ARCHE-WELLE A: BLENDER-GRUNDSTRUKTUR + 6 ZIMMERMANNS-HERO-MODULE** |
| [`L20946`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20946) | **1C. ARCHE-WELLE B: MASCHINENBAU (B1), 7.920 FÄSSER, HABITATE (B2) & MANNSCHAFTSRÄUME (B3)** |
| [`L21486`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21486) | **A) WELLE B1 — MASCHINENBAU (S4 & S11), 7.920 FÄSSER, SPEZIALRÄUME & OPTIK** |
| [`L21794`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21794) | **B) WELLE B2 — TIER-LEBENSWELTEN D1–D3, 1K-HEUBALLEN & 5 PIKTOGRAMME** |
| [`L21967`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21967) | **C) WELLE B3 — MANNSCHAFTSRÄUME FÜR NOAHS 8-KÖPFIGE FAMILIE (S7 DECK 3)** |
| [`L22047`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22047) | **2. Z-Up-Geometrie-Helfer (Z ist OBEN!) & Ausrichtungs-Funktionen** |
| [`L22078`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22078) | **3. Höhenfunktionen & Geometrie-Helfer für Steppe und Hochgebirge** |
| [`L22997`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22997) | **PROZEDURALE BOTANIK: 4-QUADRANTEN-ATLAS & 3-STUFIGE VERÄSTELUNG (PAKET 1E)** |
| [`L24689`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24689) | **3B. Ultraleichter 12-km-Fernhorizont-Ring (~1.792 Tris, 0 % Weltkante)** |
| [`L24807`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24807) | **3C. 4-Band-Schatten-LOD-Helfer (Höhentextur-Bake + Projizierte GPU-Schatten)** |
| [`L25212`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25212) | **4. Kompletter Neuaufbau des Werftplatzes (Arche.Environment.buildShipyard3D)** |
| [`L27205`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27205) | **BAUGRUPPE 1: Baumfäll-Szene im Primärwald & Rollenträger-Knechte (Kap. 13.1)** |
| [`L27461`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27461) | **BAUGRUPPE 2: Göpel-Sägewerk, drehender Rotor, Kurbelschleife & Sägegruben (Kap. 13.1)** |
| [`L27769`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27769) | **BAUGRUPPE 3: 4 Holzkohlemeiler, Tubal-Kain-Schmiede & 9 Rauchsäulen (Kap. 13.1 & 13.2)** |
| [`L33665`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33665) | **4B. ASYNCHRONE BLENDER-BOTANIK-HYDRATION (6 ARTEN x 15 VARIANTEN x LOD0/LOD1)** |
| [`L35075`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35075) | **4C. ASYNCHRONE MESOPOTAMIA-CITY-KIT-HYDRATION & 4-STUFEN-LOD (0..3000 m)** |
| [`L36084`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36084) | **4D. ASYNCHRONE SHIPYARD-INDUSTRY-KIT-HYDRATION & 4-STUFEN-LOD (0..3000 m)** |
| [`L36556`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36556) | **4E. ASYNCHRONE MENSCHEN-KIT v2.1 HYDRATION (8 NOAH-HEROES + 45 BÜRGER-VARIANTEN)** |
| [`L39206`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39206) | **3. Exakte Höhen-Synchronisation & Ausblenden des schwarzen seaGrid** |
| [`L42854`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42854) | **SYSTEM 1 (aPathType = 0.0): Vordere Frischluft-Schachtkammer & Erdregister |ZUL.|** |
| [`L42941`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42941) | **SYSTEM 2 (aPathType = 1.0 & 1.5): Stall-Durchstroemung & echte Tuer-Durchtritte** |
| [`L42983`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42983) | **SYSTEM 3 (aPathType = 2.0): Thermik, 1-Elle-Silospalt, Badgir-Lee-Kammer & Zohar** |
| [`L43156`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43156) | **SYSTEM 4 (aPathType = 3.0): Offenes 9x8-Ellen-Seitentor S7** |
| [`L50689`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L50689) | **Screen-Space Contact Shadows (SSCS, Half-Res Depth, Desktop Tier 0/1, WebGL1)** |
| [`L52878`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52878) | **SUITE 1: 1. Ellen-Kanon, EN 338 & Clean Architecture (T01–T07)** |
| [`L52927`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52927) | **SUITE 2: 2. Hydrostatik, Massenbilanz & Schwimmstabilität (T08–T18)** |
| [`L53013`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53013) | **SUITE 3: 3. Wellenkinematik & 6-DOF-Hydrodynamik (T19–T30)** |
| [`L53092`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53092) | **SUITE 4: 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik (T31–T53)** |
| [`L53325`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53325) | **SUITE 5: 5. 371-Tage-Chronik, Ermüdung & Instandhaltung (T54–T56)** |
| [`L53367`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53367) | **SUITE 6: 6. Holz-Stein-Maschinenbau, Silos & Einbauten (T57–T71)** |
| [`L53469`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53469) | **SUITE 7: 7. Meteorologie, Bauphysik & Veterinär-Physiologie (T72–T92)** |
| [`L53645`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53645) | **SUITE 8: 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität (T93–T101)** |

---

## 4. 3D-Baugruppen

### 4.1 Werftplatz & Trockendock (`buildShipyard3D`)
> Bereich: **Zeile 25214 bis 37256** (Funktion `Arche.Environment.buildShipyard3D`)

| Zeile | Typ | Baugruppe / Eigenschaft | Details |
|:-----:|:---:|:------------------------|:--------|
| [`L25218`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25218) | `userData` | **shipyardGroup.userData.cribbingBlocks** | `[];` |
| [`L25219`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25219) | `userData` | **shipyardGroup.userData.pitchPits** | `[];` |
| [`L25231`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25231) | `userData` | **shipyardGroup.userData.heightMapTex** | `bakedSy.tex;` |
| [`L25234`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25234) | `Abschnitt` | **1. Topografisches Trockendock-Becken & Quellgebirge (1600 x 1600 m, 240 x 240 Segmente)** | `` |
| [`L25260`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25260) | `userData` | **shipyardGroup.userData.basinMesh** | `terrainMesh;` |
| [`L25293`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25293) | `userData` | **shipyardGroup.userData.horizonRingMesh** | `syHorizon.mesh;` |
| [`L25294`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25294) | `userData` | **shipyardGroup.userData.horizonMat** | `syHorizon.mat;` |
| [`L25428`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25428) | `userData` | **shipyardGroup.userData.waterAquaMat** | `waterAquaMat;` |
| [`L25455`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25455) | `userData` | **shipyardGroup.userData.basaltMasonryMat** | `basaltMat;` |
| [`L25470`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25470) | `userData` | **shipyardGroup.userData.aqueductFlowMat** | `aqueductFlowMat;` |
| [`L25489`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25489) | `userData` | **shipyardGroup.userData.canalBedMat** | `canalBedMat;` |
| [`L25529`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25529) | `userData` | **shipyardGroup.userData.canalWaterBedMat** | `canalWaterBedMat;` |
| [`L25670`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25670) | `userData` | **shipyardGroup.userData.riverWaterMat** | `riverWaterMat;` |
| [`L25693`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25693) | `userData` | **shipyardGroup.userData.flagstoneMat** | `flagstoneMat;` |
| [`L25711`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25711) | `userData` | **shipyardGroup.userData.lapisFriezeMat** | `lapisFriezeMat;` |
| [`L25724`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25724) | `userData` | **shipyardGroup.userData.ochreAwningMat** | `ochreAwningMat;` |
| [`L25775`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25775) | `userData` | **shipyardGroup.userData.shipyardKitPlacements** | `shipyardKitPlacements;` |
| [`L25776`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25776) | `userData` | **shipyardGroup.userData.shipyardKitDynamic** | `shipyardKitDynamic;` |
| [`L25777`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25777) | `userData` | **shipyardGroup.userData.procShipyardMeshes** | `procShipyardMeshes;` |
| [`L25826`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25826) | `Abschnitt` | **3. Die 60-Ellen-Beladerampe zum Seitentor (Backbord @ X = -5.0 m)** | `` |
| [`L25849`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25849) | `userData` | **shipyardGroup.userData.mainRampMesh** | `deckMesh;` |
| [`L25913`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25913) | `Abschnitt` | **3. Animierte Beladungs-Karawane vor der Flut (boardingGroup)** | `` |
| [`L25917`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25917) | `userData` | **shipyardGroup.userData.boardingGroup** | `boardingGroup;` |
| [`L25919`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25919) | `userData` | **shipyardGroup.userData.boardingWalkers** | `boardingWalkers;` |
| [`L25992`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25992) | `userData` | **shipyardGroup.userData.caravanMeta** | `caravanMeta;` |
| [`L26061`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26061) | `userData` | **shipyardGroup.userData.caravanInstMesh** | `caravanInstMesh;` |
| [`L26100`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26100) | `userData` | **shipyardGroup.userData.shipyardBirdsInstMesh** | `shipyardBirdsInstMesh;` |
| [`L26103`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26103) | `userData` | **shipyardGroup.userData.impactFX** | `Arche.Fauna.createGroundImpactFX(shipyardGroup, 64, 56, false);` |
| [`L26111`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26111) | `userData` | **shipyardGroup.userData.bunkeringGroup** | `bunkeringGroup;` |
| [`L26113`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26113) | `userData` | **shipyardGroup.userData.bunkeringWalkers** | `bunkeringWalkers;` |
| [`L26125`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26125) | `userData` | **shipyardGroup.userData.sackMat** | `sackMat;` |
| [`L26249`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26249) | `Abschnitt` | **4. Zugbrücken-Klappe (drawbridgeFlapGroup)** | `` |
| [`L26277`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26277) | `userData` | **shipyardGroup.userData.bronzeToolMat** | `bronzeToolMat;` |
| [`L26284`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26284) | `userData` | **shipyardGroup.userData.smithyMetalMat** | `smithyMetalMat;` |
| [`L26323`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26323) | `userData` | **shipyardGroup.userData.mudbrickMat** | `mudbrickMat;` |
| [`L26338`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26338) | `userData` | **shipyardGroup.userData.reedThatchMat** | `reedThatchMat;` |
| [`L26348`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26348) | `userData` | **shipyardGroup.userData.dryWorkers** | `[];` |
| [`L26350`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26350) | `userData` | **shipyardGroup.userData.dryWorkerPlacements** | `_dryWorkerPlacements;` |
| [`L26392`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26392) | `userData` | **shipyardGroup.userData.scaffolds** | `[];` |
| [`L26728`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26728) | `userData` | **shipyardGroup.userData.craneWinchInstMeshes** | `_winchInstMeshes;` |
| [`L26729`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26729) | `userData` | **shipyardGroup.userData.craneOxInst** | `_craneOxInst;` |
| [`L26730`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26730) | `userData` | **shipyardGroup.userData.craneOxLocals** | `_craneOxLocals;` |
| [`L26741`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26741) | `userData` | **shipyardGroup.userData.craneHoistGroups** | `craneHoistGroups;` |
| [`L26742`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26742) | `userData` | **shipyardGroup.userData.craneWinchRotors** | `craneWinchRotors;` |
| [`L26744`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26744) | `Abschnitt` | **7. Kopher-Pechsiederei (3 Rundöfen mit glühendem Bad, Pechsiedern & Kalfater-Werkzeuglager)** | `` |
| [`L26939`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26939) | `userData` | **shipyardGroup.userData.smithyEmberMat** | `smithyEmberMat;` |
| [`L26951`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26951) | `userData` | **shipyardGroup.userData.terracottaMat** | `terracottaMat;` |
| [`L27072`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27072) | `userData` | **shipyardGroup.userData.hayMat** | `hayMat;` |
| [`L27107`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27107) | `Abschnitt` | **10. Kapitel 13: Holzriese & Rollenbahn** | `` |
| [`L27205`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27205) | `Kapitel 13 Baugruppe` | **BAUGRUPPE 1: Baumfäll-Szene im Primärwald & Rollenträger-Knechte (Kap. 13.1)** | `` |
| [`L27214`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27214) | `Abschnitt` | **1. Stehender 22-m-Zedernriese (D = 1.56 m) — nutzt leichtes Lambert-Foliage-Material statt separatem 250-Zeilen-Legacy-Programm!** | `` |
| [`L27305`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27305) | `Abschnitt` | **3. Seilzug in der Krone + Umlenkrolle + 4 Zugochsen als 2 Doppelgespanne (Kettenlinie mit Durchhang)** | `` |
| [`L27355`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27355) | `Abschnitt` | **4. Nachbar-Baumstumpf (-139.2, -96.8) & waagerecht am Boden liegender 20-m-Zedernstamm ([-138.0, -96.0] bis [-122.0, -84.0]) mit 3D-POM-Zedernborke** | `` |
| [`L27457`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27457) | `userData` | **shipyardGroup.userData.fellingSceneGroup** | `fellingSceneGroup;` |
| [`L27461`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27461) | `Kapitel 13 Baugruppe` | **BAUGRUPPE 2: Göpel-Sägewerk, drehender Rotor, Kurbelschleife & Sägegruben (Kap. 13.1)** | `` |
| [`L27472`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27472) | `Abschnitt` | **1. Basalt-Bruchsteinring (R = 4.0 m) auf dem ebenen +2.80 m Plateau** | `` |
| [`L27480`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27480) | `Abschnitt` | **2. Feststehendes Eichen-Galgenportal & Basalt-Spurlager über dem Göpel** | `` |
| [`L27490`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27490) | `Abschnitt` | **3. Drehbare Untergruppe: sawmillCapstanRotor (Königswelle, Kammrad & Joche gebatcht + 4 gehörnte Zugochsen)** | `` |
| [`L27542`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27542) | `userData` | **shipyardGroup.userData.sawmillCapstanRotor** | `sawmillCapstanRotor;` |
| [`L27544`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27544) | `Abschnitt` | **4. Drehende Vorgelegewelle mit 8er-Stockritzel, Schwungrad & Kurbelzapfen (sawDriveShaftRotor)** | `` |
| [`L27551`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27551) | `userData` | **shipyardGroup.userData.sawdustMat** | `sawdustMat;` |
| [`L27591`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27591) | `userData` | **shipyardGroup.userData.sawDriveShaftRotor** | `sawDriveShaftRotor;` |
| [`L27593`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27593) | `Abschnitt` | **5. Lagerung der Vorgelegewelle: Oberer Längsträger über der Ochsenbahn (0 % Spur-Kollision!) + Außen-Lagerbock bei x = sx0 + 4.65** | `` |
| [`L27629`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27629) | `Abschnitt` | **6. Vertikales Sägegatter mit separat gelenkter Pleuelstange (Kurbelschleife)** | `` |
| [`L27646`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27646) | `userData` | **shipyardGroup.userData.sawFrame** | `sawFrameMesh;` |
| [`L27647`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27647) | `userData` | **shipyardGroup.userData.sawFrameBaseZ** | `sz0 + 1.2;` |
| [`L27659`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27659) | `userData` | **shipyardGroup.userData.sawPitmanGroup** | `sawPitmanGroup;` |
| [`L27660`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27660) | `userData` | **shipyardGroup.userData.sawPitmanBaseZ** | `sz0 + 1.82;` |
| [`L27661`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27661) | `userData` | **shipyardGroup.userData.sawPitmanCenterY** | `sy0;` |
| [`L27662`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27662) | `userData` | **shipyardGroup.userData.sawCrankCenterZ** | `sz0 + 2.62;` |
| [`L27765`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27765) | `userData` | **shipyardGroup.userData.sawPitGroup** | `sawPitGroup;` |
| [`L27769`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27769) | `Kapitel 13 Baugruppe` | **BAUGRUPPE 3: 4 Holzkohlemeiler, Tubal-Kain-Schmiede & 9 Rauchsäulen (Kap. 13.1 & 13.2)** | `` |
| [`L27785`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27785) | `userData` | **shipyardGroup.userData.meilerDomeMat** | `meilerDomeMat;` |
| [`L27795`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27795) | `userData` | **shipyardGroup.userData.meilerHotMat** | `meilerHotMat;` |
| [`L27843`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27843) | `userData` | **shipyardGroup.userData.smokeMat** | `smokeMat;` |
| [`L27870`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27870) | `userData` | **shipyardGroup.userData.smokePlumesGroup** | `smokePlumesGroup;` |
| [`L27871`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27871) | `userData` | **shipyardGroup.userData.smokePuffs** | `smokePuffs;` |
| [`L27887`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27887) | `userData` | **shipyardGroup.userData.smithyAnvilMat** | `smithyAnvilMat;` |
| [`L27986`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27986) | `userData` | **shipyardGroup.userData.smithyToolsGroup** | `smithyToolsGroup;` |
| [`L27989`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27989) | `Abschnitt` | **13. Kapitel 13: Frischwasser-Aquädukt & Raubtier-Rollkäfige** | `` |
| [`L28248`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28248) | `userData` | **shipyardGroup.userData.cityKitPlacements** | `cityKitPlacements;` |
| [`L28249`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28249) | `userData` | **shipyardGroup.userData.roadKitProps** | `roadKitProps;` |
| [`L28250`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28250) | `userData` | **shipyardGroup.userData.procCityMeshes** | `procCityMeshes;` |
| [`L28993`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28993) | `userData` | **shipyardGroup.userData.temenosKitPlacements** | `temenosKitPlacements;` |
| [`L28994`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28994) | `userData` | **shipyardGroup.userData.procTemenosMeshes** | `procTemenosMeshes;` |
| [`L29036`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29036) | `Abschnitt` | **1. Hero-Ziggurat ("hero_ziggurat_ur") exakt auf Prozessionsachse x=210 zum Prunktor ausgerichtet (Dreifachtreppe -> -Y, nach hinten +6.5m verlängert -> Rückwand Y=+8.50m, 6.50m frei bis Nordmauer Y=+15.0m!)** | `` |
| [`L29042`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29042) | `Abschnitt` | **2. Hero-Temenos-Prunktor ("hero_temenos_gate") exakt auf der Prozessionsachse (210, -38)** | `` |
| [`L29048`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29048) | `Abschnitt` | **3. Hero-Temenos-Innenmauer ("hero_temenos_wall_seg", 6m-Modul mit -0.35m Schürze -> 0 Fundament-Z-Fighting!)** | `` |
| [`L29079`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29079) | `Abschnitt` | **4. Hero-Nebengebäude ("hero_temple_annex_01" Schatzhaus & "hero_temple_annex_02" Priester-/Archivhaus, Portikus +X zum Tempelhof!)** | `` |
| [`L29094`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29094) | `Abschnitt` | **5. Zwei monumentale 3D-Abzu-Tempelteiche ("hero_abzu_pond" + "abzu_water_surface") symmetrisch links/rechts der Prozessionsachse!** | `` |
| [`L29116`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29116) | `Abschnitt` | **6. Durchgehendes Travertin-Prozessionspflaster ("temple_paving_slab") vom Prunktor zum Vorplatz-Altar & Zikkurat-Treppe + Querachsen** | `` |
| [`L29129`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29129) | `Abschnitt` | **7. Vorplatz-Heiligtum: Monumentaler Hornaltar, 2 Sumerische Stelen & 6 Bronze-Feuerständer (castShadow = false)** | `` |
| [`L29148`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29148) | `Abschnitt` | **8. Üppiger Heiliger Hain & Tempelgärten: Gemauerte Hochbeete, Schatten-Pergolen, Tempel-Zypressen & Granatapfelbäume!** | `` |
| [`L29276`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29276) | `userData` | **shipyardGroup.userData.blenderOrnamentalSpecs** | `blenderOrnamentalSpots;` |
| [`L29631`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29631) | `userData` | **shipyardGroup.userData.organicRoadMesh** | `orgRoadMesh;` |
| [`L29632`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29632) | `userData` | **shipyardGroup.userData.organicRoadMat** | `orgRoadMat;` |
| [`L29650`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29650) | `userData` | **shipyardGroup.userData.roadMesh** | `roadMesh;` |
| [`L29651`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29651) | `userData` | **shipyardGroup.userData.roadMeshOrigMat** | `flagstoneMat;` |
| [`L29834`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29834) | `Abschnitt` | **1. Nord-Vorstadt (außerhalb Nord-Königstor bei y=+36..+52)** | `` |
| [`L29837`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29837) | `Abschnitt` | **2. Süd-Vorstadt (außerhalb Süd-Karawanentor bei y=-136..-162)** | `` |
| [`L29840`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29840) | `Abschnitt` | **3. Ostufer-Brückenkopf & Karawanserei (x=272..294, y=-68..-28)** | `` |
| [`L30304`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30304) | `userData` | **shipyardGroup.userData.cityBoats** | `cityBoats;` |
| [`L30359`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30359) | `userData` | **shipyardGroup.userData.cityWalkers** | `cityWalkers;` |
| [`L30614`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30614) | `Abschnitt` | **1. Ur-Schinar Süd & Südwest-Schwemmland (10 große Parzellen)** | `` |
| [`L30625`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30625) | `Abschnitt` | **2. Ur-Ostufer / Euphrat-Ostebene gegenüber der Metropole (10 weite Parzellen)** | `` |
| [`L30636`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30636) | `Abschnitt` | **3. Nisaba-Kornkammer / Südwest-Ebene (10 weite Parzellen)** | `` |
| [`L30647`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30647) | `Abschnitt` | **4. Eridu-Lagunengürtel / Südost-Ebene (8 große Parzellen)** | `` |
| [`L30656`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30656) | `Abschnitt` | **5. Girsu-Kanalauen / Ost-Ebene (8 weite Parzellen)** | `` |
| [`L30665`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30665) | `Abschnitt` | **6. Sippar & Nord-Euphrattal (6 große Parzellen)** | `` |
| [`L30672`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30672) | `Abschnitt` | **7. Larsam-Südoase / Süd-Weide & Getreidegürtel (6 weite Parzellen)** | `` |
| [`L30949`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30949) | `userData` | **shipyardGroup.userData.procCropInstMesh** | `cropInstMesh;` |
| [`L30950`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30950) | `userData` | **shipyardGroup.userData.blenderCropSpecs** | `{` |
| [`L31064`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31064) | `Abschnitt` | **1. Ur-Schinar Süd & SW (12)** | `` |
| [`L31071`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31071) | `Abschnitt` | **2. Ur-Ostufer gegenüber Metropole (12)** | `` |
| [`L31078`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31078) | `Abschnitt` | **3. Nisaba Kornkammer (12)** | `` |
| [`L31085`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31085) | `Abschnitt` | **4. Eridu Lagunengürtel (8)** | `` |
| [`L31090`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31090) | `Abschnitt` | **5. Girsu Ost-Ebene (8)** | `` |
| [`L31095`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31095) | `Abschnitt` | **6. Sippar & Nord-Euphrattal (6)** | `` |
| [`L31099`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31099) | `Abschnitt` | **7. Larsam Südoase (6)** | `` |
| [`L31216`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31216) | `userData` | **shipyardGroup.userData.farmInsts** | `{` |
| [`L31228`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31228) | `userData` | **shipyardGroup.userData.farmMovers** | `farmMovers;` |
| [`L31292`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31292) | `userData` | **shipyardGroup.userData.shadufInsts** | `shadufInsts;` |
| [`L31293`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31293) | `userData` | **shipyardGroup.userData.shadufBeams** | `shadufBeams;` |
| [`L31332`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31332) | `userData` | **shipyardGroup.userData.waterWheels** | `waterWheels;` |
| [`L31346`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31346) | `userData` | **shipyardGroup.userData.waterFoamMat** | `waterFoamMat;` |
| [`L31387`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31387) | `userData` | **shipyardGroup.userData.waterFoamInstMesh** | `waterFoamInstMesh;` |
| [`L31388`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31388) | `userData` | **shipyardGroup.userData.waterFoamNodes** | `foamNodes;` |
| [`L31389`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31389) | `userData` | **shipyardGroup.userData.waterFoamWakeStart** | `wakeSlotStart;` |
| [`L31404`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31404) | `userData` | **shipyardGroup.userData.cityBuildingShadowsInstMesh** | `bldgShadowInst;` |
| [`L31473`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31473) | `userData` | **shipyardGroup.userData.oarsmanInst** | `oarInst;` |
| [`L31499`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31499) | `userData` | **shipyardGroup.userData.magurInstMeshes** | `boatParts.map(p => p.inst);` |
| [`L31500`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31500) | `userData` | **shipyardGroup.userData._magurAllCount** | `_magurAll.length;` |
| [`L31501`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31501) | `userData` | **shipyardGroup.userData._magurLogCount** | `_magurLogs.length;` |
| [`L31502`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31502) | `userData` | **shipyardGroup.userData._magurCargoCount** | `_magurCargo.length;` |
| [`L31503`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31503) | `userData` | **shipyardGroup.userData.updateMagurBoatMatrix** | `(bt, mat4) => {` |
| [`L31616`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31616) | `userData` | **shipyardGroup.userData.cityWalkerInstMeshes** | `cityWalkerInstMeshes;` |
| [`L31635`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31635) | `userData` | **shipyardGroup.userData.smokeInstMesh** | `smokeInst;` |
| [`L31743`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31743) | `userData` | **shipyardGroup.userData.boulderMat** | `boulderMat;` |
| [`L31801`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31801) | `userData` | **shipyardGroup.userData.boulderInstMesh** | `boulderInstMesh;` |
| [`L31823`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31823) | `userData` | **shipyardGroup.userData.logYardMat** | `logYardMat;` |
| [`L31863`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31863) | `userData` | **shipyardGroup.userData.logYardInstMesh** | `logYardInstMesh;` |
| [`L32048`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32048) | `userData` | **shipyardGroup.userData.steppeGrassInstMesh** | `steppeGrassInstMesh;` |
| [`L32049`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32049) | `userData` | **shipyardGroup.userData.blenderGrassSpecs** | `{ count: gPlaced, transforms: gPlaceTf, kind: gPlaceKind, colors:` |
| [`L32234`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32234) | `userData` | **shipyardGroup.userData.steppeShrubInstMesh** | `shrubInstMeshes[0];` |
| [`L32235`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32235) | `userData` | **shipyardGroup.userData.shrubInstMeshes** | `shrubInstMeshes;` |
| [`L32236`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32236) | `userData` | **shipyardGroup.userData.procShrubMeshes** | `shrubInstMeshes.slice();` |
| [`L32271`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32271) | `userData` | **shipyardGroup.userData.stumpBarkMat** | `stumpBarkMat;` |
| [`L32272`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32272) | `userData` | **shipyardGroup.userData.stumpCutMat** | `stumpCutMat;` |
| [`L32321`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32321) | `userData` | **shipyardGroup.userData.treeStumps** | `stumpsGroup;` |
| [`L32830`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32830) | `userData` | **shipyardGroup.userData.treesGroup** | `treesGroup;` |
| [`L32831`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32831) | `userData` | **shipyardGroup.userData.procTreeInstMeshes** | `allTreeInstMeshes.slice();` |
| [`L32832`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32832) | `userData` | **shipyardGroup.userData.blenderForestPlacements** | `{` |
| [`L32867`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32867) | `userData` | **shipyardGroup.userData.treeShadowInstMesh** | `_syTreeShadInst;` |
| [`L32870`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32870) | `userData` | **shipyardGroup.userData.forestTrunksInstMesh** | `forestTrunksInstMesh;` |
| [`L32871`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32871) | `userData` | **shipyardGroup.userData.allTreeInstMeshes** | `allTreeInstMeshes;` |
| [`L33141`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33141) | `Abschnitt` | **1. Bäume: Echtes 4-Stufen-LOD (Desktop: 150m / 500m / 1500m / 3000m, Werft & Ararat!)** | `` |
| [`L33404`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33404) | `Abschnitt` | **2. Prüfe die Strauch-Meshes (shrubInstMeshes — bis 640 m & hartes Frustum-Culling)** | `` |
| [`L33455`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33455) | `Abschnitt` | **3. Hydrierte Blender-Unterholz-, Gras-/Schilf-, Agrar- & Tempelzierbotanik-Gruppen (Werft & Ararat + Frustum-Culling)** | `` |
| [`L33615`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33615) | `Abschnitt` | **4. Frustum- & Distanz-Culling für Werft-Handwerker (dryWorkers) & Stadtbewohner-Zone (Ur-Schinar)** | `` |
| [`L34588`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34588) | `Abschnitt` | **1. Sträucher & Euphrat-Schilf/Papyrus aus procShrubMeshes** | `` |
| [`L34617`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34617) | `Abschnitt` | **2. Steppengras & Hochgras aus blenderGrassSpecs** | `` |
| [`L34640`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34640) | `Abschnitt` | **3. Mesopotamische Kulturpflanzen & Weinreben aus blenderCropSpecs** | `` |
| [`L34661`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34661) | `Abschnitt` | **4. Tempel-, Hofgarten-, Terrakotta-Kübel- & Lotus-Zierbotanik** | `` |
| [`L34748`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34748) | `Abschnitt` | **1. Ararat-Bäume nach (species, stage, varIdx) bündeln & auf 4-LOD-Pools (150/500/1500/3000m) mappen** | `` |
| [`L34906`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34906) | `Abschnitt` | **2. Ararat Sträucher, Schilf & Pioniergras als LOD-gepoolte ExtraGroups (mit uSproutGrowth & Frustum-Culling)** | `` |
| [`L35708`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35708) | `Abschnitt` | **1. Trim-Material: teilt arche_world_trim_unified_v1 (0 neue Shader-Programme!) + glühende Altarkohle via emissiveMap!** | `` |
| [`L35717`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35717) | `Abschnitt` | **2. Botanik-Material: teilt arche_blender_botany_v5_fol (0 neue Shader-Programme!) mit identischer DUMMY_TEX-Signatur!** | `` |
| [`L35764`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35764) | `Abschnitt` | **3. Abzu-Wasseroberfläche: 1 gemeinsames reguläres Mesh mit ud.waterAquaMat (0 neue Shader-Programme, 1 Draw-Call, 0% Z-Fighting!)** | `` |
| [`L35827`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35827) | `Abschnitt` | **4. InstancedMesh-Pools für alle 14 Temenos-Architektur-, Garten- & Baum-Module (4 LODs: 150/500/1500/3000 m)** | `` |
| [`L36735`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36735) | `Abschnitt` | **1. Alle 8 Mitglieder von Noahs Familie am Ararat-Altar (1:1 Meter-Skala, scale = 1.0, sauberer Bodenkontakt!)** | `` |
| [`L37239`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37239) | `Abschnitt` | **5. Kompletter Neuaufbau des Ararat-Landeplatzes (Arche.Environment.buildAraratLandingSite3D)** | `` |

### 4.2 Ararat-Landeplatz (`buildAraratLandingSite3D`)
> Bereich: **Zeile 37257 bis 39300** (Funktion `Arche.Environment.buildAraratLandingSite3D`)

| Zeile | Typ | Baugruppe / Eigenschaft | Details |
|:-----:|:---:|:------------------------|:--------|
| [`L37261`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37261) | `userData` | **araratGroup.userData.isBuilt** | `true;` |
| [`L37262`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37262) | `userData` | **araratGroup.userData.blenderCharactersHydrated** | `false;` |
| [`L37263`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37263) | `userData` | **araratGroup.userData.saddleMesh** | `null;` |
| [`L37264`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37264) | `userData` | **araratGroup.userData.altarCoals** | `null;` |
| [`L37265`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37265) | `userData` | **araratGroup.userData.disembarkRampMesh** | `null;` |
| [`L37277`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37277) | `userData` | **araratGroup.userData.heightMapTex** | `bakedAra.tex;` |
| [`L37280`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37280) | `Abschnitt` | **1. Integriertes Hochgebirgs- & Sattel-Mesh (1.400 x 1.400 m, 208 x 208 Segmente mit zentrierter Auflösungs-Verdichtung für glatte Gipfelgrate & bündigen Kielsattel)** | `` |
| [`L37308`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37308) | `userData` | **araratGroup.userData.saddleMesh** | `terrainMesh;` |
| [`L37336`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37336) | `userData` | **araratGroup.userData.horizonRingMesh** | `araHorizon.mesh;` |
| [`L37337`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37337) | `userData` | **araratGroup.userData.horizonMat** | `araHorizon.mat;` |
| [`L37403`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37403) | `userData` | **araratGroup.userData.basaltCragsInstMesh** | `cragInst;` |
| [`L37525`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37525) | `userData` | **araratGroup.userData.waterfallGroup** | `waterfallGroup;` |
| [`L37526`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37526) | `userData` | **araratGroup.userData.waterfallUniforms** | `waterfallUniforms;` |
| [`L37528`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37528) | `Abschnitt` | **2. Fels-, Holz-, Feuer- & Bronzezeit-Materialien (alle WebGL1 AAA-gekoppelt & Thermo-/Struktur-fähig)** | `` |
| [`L37587`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37587) | `Abschnitt` | **3. Ausschiffungs-Steg & 4-stufiger Baufortschritt (rampStages) mit Catenary-Hanfseilen & Zimmermannsholz** | `` |
| [`L37691`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37691) | `userData` | **araratGroup.userData.rampCarpenterMeshes** | `rampCarpenterMeshes;` |
| [`L37842`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37842) | `userData` | **araratGroup.userData.rampStages** | `{` |
| [`L37848`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37848) | `userData` | **araratGroup.userData.disembarkRampMesh** | `gangwayDeck;` |
| [`L37854`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37854) | `Abschnitt` | **4. Großer Zyklopischer Dankopfer-Altar (Gen 8,20 / Ex 20,25), Opferfeuer (~600°C Thermo) & Noahs gesamte Familie (8 Personen)** | `` |
| [`L37925`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37925) | `userData` | **araratGroup.userData.altarStoneGroup** | `altarStoneGroup;` |
| [`L37939`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37939) | `userData` | **araratGroup.userData.altarCoals** | `coalMesh;` |
| [`L37963`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37963) | `userData` | **araratGroup.userData.uAltarFireThermo** | `uAltarFireThermo;` |
| [`L37964`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37964) | `userData` | **araratGroup.userData.uAltarFlicker** | `uAltarFlicker;` |
| [`L37990`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37990) | `userData` | **araratGroup.userData.altarEmberGlow** | `altarEmberGlow;` |
| [`L37997`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37997) | `userData` | **araratGroup.userData.altarFlickerLight** | `altarFlickerLight;` |
| [`L37999`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37999) | `Abschnitt` | **1. Volumetrisches fBm-Schwarzkörper-Opferfeuer (7 gekreuzte Flammen-Flächen = 1 Draw-Call, WebGL1-konform)** | `` |
| [`L38122`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38122) | `userData` | **araratGroup.userData.altarFlames** | `altarFlames;` |
| [`L38124`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38124) | `Abschnitt` | **2. Aufsteigende Funken & Glut-Asche (45 Funken in 1 THREE.Points Draw-Call, rein im Shader animiert)** | `` |
| [`L38189`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38189) | `userData` | **araratGroup.userData.altarSparks** | `altarSparks;` |
| [`L38191`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38191) | `Abschnitt` | **3. Weicher prozeduraler Opferrauch (Noise-Alpha-Billboards, keine harten Kugel-Silhouetten!)** | `` |
| [`L38270`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38270) | `userData` | **araratGroup.userData.altarSmokePuffs** | `altarSmokePuffs;` |
| [`L38305`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38305) | `userData` | **araratGroup.userData.altarFamilyEntries** | `altarFamilyEntries;` |
| [`L38306`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38306) | `userData` | **araratGroup.userData.altarGroup** | `altarGroup;` |
| [`L38309`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38309) | `Abschnitt` | **5. Kreativ-Highlight: Bronzezeitliches Basislager am Stegfuß (Terrakotta-Amphoren, Zedernkiste, Werkzeuge, Hanftau — mat zuerst!)** | `` |
| [`L38365`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38365) | `userData` | **araratGroup.userData.campGroup** | `campGroup;` |
| [`L38388`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38388) | `userData` | **araratGroup.userData.svalbardPlotGroup** | `svalbardPlotGroup;` |
| [`L38391`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38391) | `Abschnitt` | **6. Kreativ-Highlight: Schimmernde Gletscher-Schmelzwasser-Tümpel & Südtal-Tränkelagunen** | `` |
| [`L38424`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38424) | `userData` | **araratGroup.userData.meltwaterGroup** | `meltwaterGroup;` |
| [`L38463`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38463) | `userData` | **araratGroup.userData.strandedMatsGroup** | `strandedMatsGroup;` |
| [`L38464`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38464) | `userData` | **araratGroup.userData.matCentersAra** | `matCentersAra;` |
| [`L38467`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38467) | `Abschnitt` | **7. Weiträumige Auswanderungs-Korridore & Herden-Verteilung über das gesamte Ararat-Massiv (Kap. 14.5)** | `` |
| [`L38613`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38613) | `userData` | **araratGroup.userData.plateauQuadInstMesh** | `plateauQuadInstMesh;` |
| [`L38614`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38614) | `userData` | **araratGroup.userData.plateauMovers** | `plateauMovers;` |
| [`L38615`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38615) | `userData` | **araratGroup.userData.plateauFaunaGroup** | `plateauFaunaGroup;` |
| [`L38618`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38618) | `Abschnitt` | **8. Kreativ-Highlight: Taube mit Ölzweig (0), Rabe (1) + 42-Vögel-Schwarm aus Himmelsdeck / Zohar in freier Bergthermik (Kap. 14.5 Phase 1)** | `` |
| [`L38658`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38658) | `userData` | **araratGroup.userData.avianFlyInstMesh** | `avianFlyInstMesh;` |
| [`L38692`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38692) | `userData` | **araratGroup.userData.doveSprigGroup** | `doveSprigGroup;` |
| [`L38699`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38699) | `userData` | **araratGroup.userData.doveHeroAnchor** | `doveHeroAnchor;` |
| [`L38714`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38714) | `Abschnitt` | **9. Kreativ-Highlight: Regenbogen-Bundesbogen hoch & weit am Himmel HINTER dem Ararat-Massiv (Gen 9,13, 0% Bergschnitt!)** | `` |
| [`L38780`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38780) | `userData` | **araratGroup.userData.rainbowArcMesh** | `rainbowArcMesh;` |
| [`L38781`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38781) | `userData` | **araratGroup.userData.rainbowUniforms** | `rainbowUniforms;` |
| [`L38785`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38785) | `userData` | **araratGroup.userData.impactFX** | `Arche.Fauna.createGroundImpactFX(araratGroup, 64, 56, true);` |
| [`L38953`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38953) | `userData` | **araratGroup.userData.sproutGrassMesh** | `araratSproutGrassInstMesh;` |
| [`L38956`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38956) | `Abschnitt` | **11. Echte botanische Werft-Vegetation + Ovoli-Olivenstümpfe & Schilf auf Ararat (Kap. 15.3–15.6)** | `` |
| [`L39073`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39073) | `userData` | **araratGroup.userData.procAraTreeMeshes** | `_procAraTreeMeshes;` |
| [`L39074`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39074) | `userData` | **araratGroup.userData.blenderAraratHydrated** | `false;` |
| [`L39075`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39075) | `userData` | **araratGroup.userData.blenderAraratSpecs** | `[` |
| [`L39136`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39136) | `userData` | **araratGroup.userData.procAraAllMeshes** | `floraInstMeshes.slice();` |
| [`L39137`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39137) | `userData` | **araratGroup.userData.blenderAraratSpecs** | `araratGroup.userData.blenderAraratSpecs.concat(araShrubSpecs);` |
| [`L39160`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39160) | `userData` | **araratGroup.userData.ovoliShootsGroup** | `ovoliShootsGroup;` |
| [`L39191`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39191) | `userData` | **araratGroup.userData.treeShadowInstMesh** | `_araTreeShadInst;` |
| [`L39195`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39195) | `userData` | **araratGroup.userData.oliveSaplingsGroup** | `araratOliveSaplingsGroup;` |
| [`L39196`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39196) | `userData` | **araratGroup.userData.floraInstMeshes** | `floraInstMeshes;` |
| [`L39197`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39197) | `userData` | **araratGroup.userData.oliveSaplings** | `[];` |
| [`L39198`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39198) | `userData` | **araratGroup.userData.themedMats** | `themedMatsAra;` |
| [`L39206`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39206) | `Abschnitt` | **3. Exakte Höhen-Synchronisation & Ausblenden des schwarzen seaGrid** | `` |

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
| [`L6300`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6300) | `Arche.Procedural.bindGpuShader(material, fixedMatId = 1)` |
| [`L6475`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6475) | `Arche.Procedural.bindEnvUniforms(shader)` |
| [`L6483`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6483) | `Arche.Procedural.injectEnvFogAndCloud(fragShader, worldPosExpr, applyCloudShadow = true, horizonShadowExpr = '')` |
| [`L6511`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6511) | `Arche.Procedural.bindMechPomShader(colorHex, mechType = 1)` |
| [`L6696`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6696) | `Arche.Procedural.cloneNoDeckClipMat(srcMat)` |
| [`L10502`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L10502) | `Arche.Procedural.buildBeddingAlphaShellTexture()` |
| [`L10587`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L10587) | `Arche.Procedural.buildVerticalHayFinTexture()` |
| [`L14769`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L14769) | `Arche.Procedural.setBucketFixturesWaveBMask(mask)` |
| [`L14815`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L14815) | `Arche.Procedural.updateInstancedBarrelsShader(ctx)` |
| [`L15795`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15795) | `Arche.Procedural.updateDrivetrainAndGalleyVisuals(ctx, fixRes, shiftState)` |
| [`L19334`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19334) | `Arche.Procedural.updateStormShutters3D(v_roof_kmh, mu_wind_rad, precip_mmh, ctx)` |
| [`L24462`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24462) | `Arche.Procedural.makeEnvMat(cacheKey, baseHex, rough, metal, fragExtraGLSL, options = {})` |
| [`L42802`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42802) | `Arche.Procedural.rebuildAirflow3DGeometry()` |
| [`L46615`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46615) | `Arche.Procedural.tempToHeatmapRGB(tempC)` |

### 5.2 Arche.Environment (Werft, Ararat & Botanik)

| Zeile | Funktion / Signatur |
|:-----:|:--------------------|
| [`L7058`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L7058) | `Arche.Environment.loadTerrainTextures()` |
| [`L7212`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L7212) | `Arche.Environment._decodeUint16PngToFloat32(arrayBuf, zMin, zMax)` |
| [`L7285`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L7285) | `Arche.Environment.syncBlenderWorlds3D()` |
| [`L7348`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L7348) | `Arche.Environment.loadBlenderWorldMaps(opts = {})` |
| [`L10792`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L10792) | `Arche.Environment.heightTexUniforms(()` |
| [`L19476`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19476) | `Arche.Environment.updateDeckSlicePlaneWorld()` |
| [`L22049`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22049) | `Arche.Environment.createZUpCylinderGeo(rTop, rBot, heightZ, segs = 12)` |
| [`L22056`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22056) | `Arche.Environment.addStrutBetweenPoints(parentGroup, p0, p1, rBot = 0.12, rTop = 0.12, mat = null, tooltipKey = null)` |
| [`L22113`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22113) | `Arche.Environment.evalRiverCenterX(y)` |
| [`L22119`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22119) | `Arche.Environment.evalRiverHalfWidth(y)` |
| [`L22124`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22124) | `Arche.Environment.evalRiverSurfaceZ(y)` |
| [`L22132`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22132) | `Arche.Environment.evalApproachRoadX(y)` |
| [`L22169`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22169) | `Arche.Environment.evalLakeLobeRadiusFrac(lake, x, y)` |
| [`L22179`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22179) | `Arche.Environment.evalLakeShorePoint(lake, ang, rFrac = 1.0)` |
| [`L22187`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22187) | `Arche.Environment.evalAlluvialLakeField(x, y)` |
| [`L22197`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22197) | `Arche.Environment.evalDistToPolyline(x, y, pts)` |
| [`L22211`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22211) | `Arche.Environment.evalCanalField(x, y)` |
| [`L22235`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22235) | `Arche.Environment._sampleBlenderHeightmapBilinear(hm, x, y)` |
| [`L22251`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22251) | `Arche.Environment.evalShipyardTerrainZ(x, y)` |
| [`L22401`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22401) | `Arche.Environment.evalAraratTerrainZ(x, y)` |
| [`L23000`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23000) | `Arche.Environment.getOrientalFoliageAtlasTex()` |
| [`L23214`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23214) | `Arche.Environment.pushLimb(buf, p0, p1, r0, r1, nSegs, rCol, gCol, bCol)` |
| [`L23272`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23272) | `Arche.Environment.pushFoliageCluster(buf, cx, cy, cz, rx, ry, rz, quadIdx, rCol, gCol, bCol, nCards = 9)` |
| [`L23331`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23331) | `Arche.Environment.pushPalmFrondRibbon(buf, spinePts, wStart, wMax, wEnd, rCol, gCol, bCol)` |
| [`L23393`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23393) | `Arche.Environment.createOrientalTreeGeo(speciesIdx, variantIdx)` |
| [`L23753`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23753) | `Arche.Environment.createOrientalShrubGeo(shrubType)` |
| [`L23847`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23847) | `Arche.Environment.getBotanyThicknessTex()` |
| [`L23878`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23878) | `Arche.Environment.applyOrientalFoliageShader(mat, options = {})` |
| [`L24691`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24691) | `Arche.Environment.createHorizonTerrainRing(opts)` |
| [`L24809`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24809) | `Arche.Environment.bakeTerrainHeightTex(evalLocalZFn, halfSpan = 3000.0, res = 256)` |
| [`L24845`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24845) | `Arche.Environment.getTreeShadowBlobTex()` |
| [`L24890`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L24890) | `Arche.Environment.createProjectedTreeShadowsMesh(treesList, evalTerrainZFn, opts = {})` |
| [`L25040`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25040) | `Arche.Environment.createProjectedBuildingShadowsMesh(bldgBoxes, evalTerrainZFn, opts = {})` |
| [`L25162`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25162) | `Arche.Environment.evalShipyardHorizonZ(wx, wy, uRadOpt, isSkirtOpt)` |
| [`L25187`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25187) | `Arche.Environment.evalAraratHorizonZ(wx, wy, uRadOpt, isSkirtOpt)` |
| [`L25214`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25214) | `Arche.Environment.buildShipyard3D()` |
| [`L32921`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32921) | `Arche.Environment.updateVegetationLOD(cam, forceUpdate = false)` |
| [`L34017`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34017) | `Arche.Environment.registerBotanySpecies(speciesKey, opts = {})` |
| [`L34022`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34022) | `Arche.Environment.loadBotanyPlantPack(speciesKey, glbUrl, opts = {})` |
| [`L34036`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34036) | `Arche.Environment.applyBotanyShaderToObject(rootObj, opts = {})` |
| [`L34077`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34077) | `Arche.Environment.loadBlenderBotanyPacks()` |
| [`L34137`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34137) | `Arche.Environment._mergeShadowProxyGeo(parts)` |
| [`L34177`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34177) | `Arche.Environment._allocTreeShadowProxyPool(cap, archKey, refSp, packsMap, parentGrp, poolList, poolMap, meshAcc, tooltipKey, depthMat, namePrefix)` |
| [`L34215`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34215) | `Arche.Environment.hydrateBlenderForest3D(packsMap)` |
| [`L34451`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34451) | `Arche.Environment.hydrateBlenderExtraBotany3D(packsMap)` |
| [`L34689`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L34689) | `Arche.Environment.hydrateBlenderAraratFlora3D(packsMap)` |
| [`L35056`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35056) | `Arche.Environment.hydrateBlenderBotany3D()` |
| [`L35321`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35321) | `Arche.Environment.hydrateMesopotamiaCityKit3D()` |
| [`L35931`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35931) | `Arche.Environment.updateCityLOD(cam, forceUpdate = false)` |
| [`L36100`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36100) | `Arche.Environment.hydrateShipyardIndustryKit3D()` |
| [`L36441`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36441) | `Arche.Environment.updateShipyardIndustryLOD(cam, forceUpdate = false)` |
| [`L36776`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36776) | `Arche.Environment.hydrateBlenderCharactersArarat3D()` |
| [`L36784`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36784) | `Arche.Environment.hydrateBlenderCharacters3D()` |
| [`L37086`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37086) | `Arche.Environment.updateCharactersLOD(cam, forceUpdate = false)` |
| [`L37168`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37168) | `Arche.Environment.updateWalkingCharactersLOD(cam, walkers, isDryCity)` |
| [`L37241`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37241) | `Arche.Environment.ensureAraratBuilt()` |
| [`L37257`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L37257) | `Arche.Environment.buildAraratLandingSite3D()` |
| [`L39214`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39214) | `Arche.Environment.evalShipyardAbsTerrainZ(x, y)` |
| [`L39218`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39218) | `Arche.Environment.evalAraratAbsTerrainZ(x, y)` |
| [`L39223`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39223) | `Arche.Environment.evalTerrainBaseAbsNN(day)` |
| [`L39234`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39234) | `Arche.Environment.evalWaterLevelAbsNN(day)` |
| [`L39280`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39280) | `Arche.Environment.evalAbsoluteElevationCouple(wAbsNN, siteBaseNN, T_mean, hExtKeel)` |
| [`L39293`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39293) | `Arche.Environment.evalWaterRiseOffset(depth, T_mean, wAbsOverride, siteBaseOverride)` |
| [`L39301`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L39301) | `Arche.Environment.updateLandmarksAndTerrain3D(depth, T_mean, dynHeaveZ, isThermalMode, isTexturedMode)` |
| [`L41129`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41129) | `Arche.Environment.updateFloatingMats3D(depth, waterRiseOffset, simTime, k, k_x, k_y, halfH, phi_rad, omega, wModel, mu_wind_rad, v_wind_ms, matsFrac, showWat)` |
| [`L50203`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L50203) | `Arche.Environment.updateHullWaterFilm3D(depth, dt_sim, isThermalMode)` |

### 5.3 Arche.Fauna (Organische Tiere, Ochsen & Knechte)

| Zeile | Funktion / Signatur |
|:-----:|:--------------------|
| [`L15997`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15997) | `Arche.Fauna.subdivideCatmullPts(pts, subdiv = 2)` |
| [`L16021`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16021) | `Arche.Fauna.buildOrganicLoftGeometry(tubes, radSegs = 20, subdiv = 2)` |
| [`L16088`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16088) | `Arche.Fauna.buildPbrMaps()` |
| [`L16151`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16151) | `Arche.Fauna.getMorphTypeForGenusId(genusId)` |
| [`L16170`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16170) | `Arche.Fauna.getFaunaBoardingHeaderGLSL(isDepthPass = false)` |
| [`L16361`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16361) | `Arche.Fauna._getArchetypeUniformValues(archetypeMode = 'QUAD')` |
| [`L16371`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16371) | `Arche.Fauna.getFaunaNormalDeformGLSL()` |
| [`L16437`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16437) | `Arche.Fauna.getFaunaVertexDeformGLSL(archetypeMode = 'QUAD', isDepthPass = false)` |
| [`L16939`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16939) | `Arche.Fauna.createFaunaDepthMaterial(archetypeMode = 'QUAD', locoScaleUniform = null, coatTypeId = 0.0)` |
| [`L16974`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L16974) | `Arche.Fauna.createFaunaMaterial(rough = 0.62, baseHex = 0xffffff, coatClass = 'FUR', archetypeMode = 'QUAD', texOverrides = null)` |
| [`L17237`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17237) | `Arche.Fauna.createGroundImpactFX(parentGroup, maxPuffs = 64, maxRings = 56, isBasalt = false)` |
| [`L17399`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17399) | `Arche.Fauna.buildSculptedLimb(xHip, yHip, zHip, lenZ, rTop, rKnee, rHoof, cHide, isHind = false)` |
| [`L17413`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17413) | `Arche.Fauna.addHeadDetails(tubes, yEye, zEye, wHead, yEar, zEar, earW, earL, cIvory, hornType = 'BOVINE')` |
| [`L17465`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17465) | `Arche.Fauna.initArchetypesAndGoepelOxen()` |
| [`L17841`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17841) | `Arche.Fauna.getGenusInfo(genusId)` |
| [`L17876`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L17876) | `Arche.Fauna.populateAllDecks()` |
| [`L18397`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18397) | `Arche.Fauna.resolveCollisionsAndClearCorridors()` |
| [`L18668`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18668) | `Arche.Fauna.syncVisibilityAndClip(zSliceMax)` |
| [`L18695`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18695) | `Arche.Fauna.updateShaderAndColors(ctx)` |
| [`L45310`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45310) | `Arche.Fauna.getIndividualHoverTooltip(ttKey, localPt, mode)` |

### 5.4 Arche.Physics (Wellen, Ozean, Mikroklima & Schichtpläne)

| Zeile | Funktion / Signatur |
|:-----:|:--------------------|
| [`L15614`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15614) | `Arche.Physics.evaluateGoepelShiftSchedule(timeOfDayHrs, isScheduleActive = false, overrideMode = null)` |
| [`L15646`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15646) | `Arche.Physics.evaluateArkTaxonomicCensus(payloadFrac = 1.0)` |
| [`L19264`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19264) | `Arche.Physics.evaluateShutterAerodynamics(headModeStr, v_roof_ms, rho_air, precip_mmh, isFullShipZohar = true, isBadgirActive = true, out = _shutterAeroScratch)` |
| [`L52468`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52468) | `Arche.Physics.evalWorldGroundSDF(wx, wy, wz)` |
| [`L52644`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52644) | `Arche.Physics.sampleMicroclimateAt(xShip, yShip, zShip, out = _microclimateScratch)` |
| [`L52730`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52730) | `Arche.Physics.evaluateAirflowVelocityField(xShip, yShip, zShip, out = _airflowVelScratch)` |

### 5.5 Arche.Performance & Quality-Governor

*Keine direkten Funktionsdeklarationen in dieser Sektion.*

### 5.6 Arche.UI & Bilinguale Tooltips

| Zeile | Funktion / Signatur |
|:-----:|:--------------------|
| [`L45442`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45442) | `Arche.UI.get3DHoverTooltipByMode(ttKey, localPt, overrideShaderMode = null)` |
| [`L45900`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45900) | `Arche.UI.getTooltip(key, lang = params.language, mode = Arche.State.viewShader, localPt = null)` |

### 5.7 Arche.Player & Kamera-Steuerung

| Zeile | Funktion / Signatur |
|:-----:|:--------------------|
| [`L52502`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52502) | `Arche.Player.flyTo(posArr, targetArr, durationSec = 1.25)` |
| [`L52517`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52517) | `Arche.Player.updateCameraAndLabels()` |

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
| [`L6705`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6705) | `orientCylinderUVsAlongAxis(geo, lengthM, radiusM)` |
| [`L6718`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6718) | `mergeTransformedGeos(entries)` |
| [`L6776`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6776) | `mergeRigidChildrenByMaterial(grp, excludeSet = null)` |
| [`L6828`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6828) | `createLanternPinionMesh(radius, length, nStaves, axis, diskMat, staveMat)` |
| [`L6857`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6857) | `createCrownWheelMesh(radius, rimThick, nTeeth, axis, toothSign, rimMat, toothMat)` |
| [`L6887`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6887) | `createArchimedeanHelixGeometry(rInner, rOuter, length, nTurns, radialSegs = 180)` |
| [`L6915`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L6915) | `createWoodenDogClutchGroup(axis, hornbeamMat, oakMat)` |
| [`L8795`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8795) | `_computeTierAnisotropy(tierIdx)` |
| [`L8806`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8806) | `applyCleanTextureFiltering(tex, isColor)` |
| [`L8822`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8822) | `syncTextureAnisotropy(tierIdx)` |
| [`L8866`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8866) | `hasGLTFLoader()` |
| [`L8870`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8870) | `_getGLTFLoader(options)` |
| [`L8890`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8890) | `_isFileProtocol()` |
| [`L8894`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8894) | `_decodeBundleEntry(entry)` |
| [`L8914`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8914) | `_computeAssetModeColor(mat, viewShader, tEnv)` |
| [`L8930`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L8930) | `attachArcheMaterialHooks(mat, options = {})` |
| [`L9207`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9207) | `syncViewShader(viewShader, tEnv)` |
| [`L9221`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9221) | `_parseGLTFBuffer(loader, arrayBuffer, resourcePath)` |
| [`L9236`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9236) | `_loadRawGLTFScene(slotKey, url, options = {})` |
| [`L9274`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9274) | `_applyTransformOpt(vec3Obj, val)` |
| [`L9281`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9281) | `_findManifestMeta(slotKey)` |
| [`L9296`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9296) | `loadGLBSlot(slotKey, url, targetParent, options = {})` |
| [`L9424`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9424) | `_isPlaceholderAlive(placeholder)` |
| [`L9434`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9434) | `_pruneStaleTargets(slotKey)` |
| [`L9448`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9448) | `_tryMountTarget(entry)` |
| [`L9533`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9533) | `registerReplaceTarget(slotKey, proceduralPlaceholderGroup, mountConfig = {})` |
| [`L9560`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9560) | `restoreProceduralFallback(slotKey)` |
| [`L9582`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9582) | `mountAllRegisteredSlots()` |
| [`L9595`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9595) | `initManifest(manifestUrl = 'assets/manifest.json')` |
| [`L9615`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9615) | `getStatus()` |
| [`L9634`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9634) | `extractInstancedTemplate(glbScene, options = {})` |
| [`L9693`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9693) | `createInstancedMesh(templateOrScene, maxCount, options = {})` |
| [`L9731`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9731) | `registerManagedMaterial(mat, options = {})` |
| [`L9754`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L9754) | `configureSmoothLODGroup(lodGroup, opts = {})` |
| [`L12022`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12022) | `createLayerBucket()` |
| [`L12041`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12041) | `woodKeyToTexIdx(woodKey)` |
| [`L12048`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12048) | `resolvePartDynamicTexIdx(bucket, x, y, z, nx, ny, nz, elemType, matType, fixTag, forceTexIdx)` |
| [`L12092`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12092) | `addQuadToBucket(bucket, p1, p2, p3, p1_dup, p3_dup, p4, nx, ny, nz, elemType, matType, fixTag = 0,...)` |
| [`L12142`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12142) | `refreshAllWoodMaterialGroups()` |
| [`L12181`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12181) | `addBoxToBucket(bucket, x0, x1, y0, y1, z0, z1, elemType, matType, fixTag = 0, forceTexIdx = -1)` |
| [`L12189`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12189) | `addThickQuadToBucket(bucket, p1, p2, p3, p4, dx, dy, dz, nx, ny, nz, elemType, matType, fixTag = 0)` |
| [`L12206`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12206) | `addStormShutterInstance(xShip, yShip, zHinge, spanW, chordH, sideDir, isBadgirFlap = false)` |
| [`L12218`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12218) | `addHorizontalBarrelCylinderRow(bucket, wireArr, x0, x1, yCenter, zCenter, radius, nSegs, fixTag = 3)` |
| [`L12224`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12224) | `addBoneTimberInstance(x0, y0, z0, x1, y1, z1, radius)` |
| [`L12235`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12235) | `addVolumetricBeddingZone(x0, x1, y0, y1, zBase, thicknessZ, moundPeakZ = 0.0, densityWeight = 1.0)` |
| [`L12245`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12245) | `buildVolumetricHullWallsAndDecks()` |
| [`L12269`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12269) | `addDeckBayWithCutout(x0, x1, y0, y1, z0, z1, cX0, cX1, cY0, cY1, matType, addGuardrail = false, openXSi...)` |
| [`L12876`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L12876) | `addWireBox(x0, x1, y0, y1, z0, z1)` |
| [`L13117`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L13117) | `addBarrelPerpendicularToWallY(bucket, wireArr, xCenter, y0, y1, zCenter, radius, nSegs, fixTag = 3, cutawayHide ...)` |
| [`L13134`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L13134) | `addTransverseBulkheadBarrelRack(xR0, xR1, yRack0, yRack1, zKantTop, zDeck, rowCountsZ, forceColsY = 0)` |
| [`L13165`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L13165) | `addChineWallBarrelRack(xCh0, xCh1, yCh0, yCh1, zDeck, isPortSide, nColsX = 5, nRowsY = 2)` |
| [`L13225`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L13225) | `addDeck1MegafaunaStallRow(xM0, xM1, yBack, yFront, nStalls, skipWaveBSpec = false)` |
| [`L13315`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L13315) | `addFlushChuteSlottedOakGrating3D(xG0, xG1, yC0, yC1, zDeck)` |
| [`L13332`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L13332) | `addOpenFlushChute3D(x0, x1, y0, y1, zDeck)` |
| [`L13555`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L13555) | `addDeck2AnimalPenRow(xP0, xP1, yBack, yFront, nPens, hasMezz = true)` |
| [`L13770`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L13770) | `addDeck3AviaryBlock(xA0, xA1, y0, y1, nCages)` |
| [`L13849`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L13849) | `addDeck3RodentHoneycombBlock(xR0, xR1, yShelf, nCols, halfDepthY = 0.35)` |
| [`L14454`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L14454) | `buildGeometryMaterialGroups(geo, metaList, excludeWaveMask = 0)` |
| [`L14674`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L14674) | `pushBedShellQuad(p1, p2, p3, p4, u0, v0, u1, v1, hLay0, hLay1 = hLay0)` |
| [`L14931`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L14931) | `createGoepelWheelGroup(xCenter)` |
| [`L15437`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15437) | `createAnimatedPaternosterGroup(xCenter)` |
| [`L15575`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15575) | `updatePaternosterAnimation(pGroup, liftPhase)` |
| [`L15659`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15659) | `setDogClutchVisualState(clutchGrp, engaged)` |
| [`L15686`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L15686) | `updateGoepelTransmissionKinematics(gMaster, deltaAngleRad, shiftState = null)` |
| [`L18815`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18815) | `writeSiloConeCell(cellIdx, x0, x1, y0, y1, zE00, zE10, zE11, zE01, xM, yM, zApex, rA, gA, bA, rE, gE...)` |
| [`L18840`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18840) | `writeTkWatQuad(qIdx, p1x, p1y, p1z, p2x, p2y, p2z, p3x, p3y, p3z, p4x, p4y, p4z, nx, ny, nz, rT, ...)` |
| [`L18868`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18868) | `updateSiloGrainAndHighTanks3D(H_silo_fill_m, d3TankFillFrac, d2SpuelFillFrac, rollRad, pitchRad, isThermalMode, ...)` |
| [`L18958`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L18958) | `buildSloshingTankVolume(x0, x1, y0, y1, zBot, zMeanWat, rTop, gTop, bTop, rBot, gBot, bBot, phaseOff)` |
| [`L19073`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19073) | `writeBilgeQuad(qIdx, p1x, p1y, p1z, p2x, p2y, p2z, p3x, p3y, p3z, p4x, p4y, p4z, nx, ny, nz, rT, ...)` |
| [`L19093`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19093) | `getDoubleBottomChamberType(iSec, jBay)` |
| [`L19104`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19104) | `updateBilgeWater3D(h_bilge_eff, rollRad, pitchRad, isThermalMode, T_bilge_C, T_sea_C)` |
| [`L19212`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19212) | `pushShutterBox(x0, x1, y0, y1, z0, z1, uScale = 1.0, vScale = 1.0)` |
| [`L19491`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19491) | `updateLayerVisibilities()` |
| [`L19679`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19679) | `writeVolRestQuad(posArr, colArr, quadIdx, xA, yA, xB, yB, rTop, gTop, bTop, rBot, gBot, bBot)` |
| [`L19940`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L19940) | `spawnSplashParticle(wx, wy, wz, vx, vy, vz, pSize = 1.6, lifeDur = 1.0, jitterXY = 1.6)` |
| [`L20104`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20104) | `updateGate3D(mode)` |
| [`L20238`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20238) | `_loadTexAsync(loader, url, isColor)` |
| [`L20254`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20254) | `_loadWoodLibraryTextures()` |
| [`L20274`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20274) | `_applyWoodSetToMat(mat, libKey)` |
| [`L20283`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20283) | `syncArkBaseWoodMaterials()` |
| [`L20328`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20328) | `_prepareArkGeometry(rawGeo, bakeZUp)` |
| [`L20340`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20340) | `_createArkStandardMaterial(srcMat, slotName)` |
| [`L20375`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20375) | `_collectLodGroupsFromScene(rawScene)` |
| [`L20401`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20401) | `rebuildArkCarpentryInstances()` |
| [`L20558`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20558) | `updateArkBadgirCaps(pairStations, zTop, isActiveTowers)` |
| [`L20586`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20586) | `syncArkWaveAVisibility(cullModeOverride)` |
| [`L20667`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20667) | `updateArkWaveALODs(cam, force)` |
| [`L20712`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20712) | `hydrateArkWaveAKits3D()` |
| [`L20990`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L20990) | `_loadTexAsyncWB(loader, url, isColor)` |
| [`L21006`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21006) | `_prepGeoWB(rawGeo, bakeZUp = true)` |
| [`L21019`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21019) | `_collectWaveBNodes(sceneRoot)` |
| [`L21046`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21046) | `_ensureTrimMaterial(fallbackScene)` |
| [`L21086`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21086) | `_ensureHayStrawMaterial()` |
| [`L21124`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21124) | `_buildHeroLODGroup(lodMap, baseName, mat, ttKey)` |
| [`L21167`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21167) | `_buildInstancedFromNode(lodMap, baseName, matrices, mat, ttKey, parentGrp, preferLod = 0)` |
| [`L21188`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21188) | `_makeMatrix(px, py, pz, rx, ry, rz, sx, sy, sz)` |
| [`L21197`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21197) | `_preparePaternosterFrameGeo(rawGeo)` |
| [`L21225`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21225) | `syncArkWaveBBarrelsCount()` |
| [`L21271`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21271) | `syncArkWaveBVisibility(cullModeOverride)` |
| [`L21384`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21384) | `updateArkWaveBLODs(cam, force = false)` |
| [`L21419`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21419) | `syncArkWaveBMachineryInstances()` |
| [`L21457`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L21457) | `hydrateArkWaveBKits3D()` |
| [`L22543`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22543) | `createGrassTuftGeo(h = 0.40, nBlades = 5, wBase = 0.12, wTop = 0.035)` |
| [`L22572`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22572) | `createShrubClusterGeo()` |
| [`L22616`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22616) | `createStaticGeometryBatcher()` |
| [`L22619`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22619) | `getBuffers(mat)` |
| [`L22628`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22628) | `addBox(mat, cx, cy, cz, sx, sy, sz, rx = 0, ry = 0, rz = 0)` |
| [`L22635`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22635) | `rotXform(x, y, z)` |
| [`L22645`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22645) | `rotNorm(nx, ny, nz)` |
| [`L22677`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22677) | `addStrut(mat, p0, p1, rTop, rBot, nSegs = 6)` |
| [`L22726`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22726) | `addCatenaryRope(mat, p0, p1, radius = 0.02, sagM = 0.14, nSteps = 12, nRadSegs = 6, windAmp = 0.035)` |
| [`L22823`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22823) | `addTentClothPanel(mat, cx, cy, cz, widthX, slopeL, rotX, nSegX = 12, nSegY = 6, rotZ = 0.0)` |
| [`L22831`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22831) | `evalPt(u, v)` |
| [`L22852`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22852) | `addGeometry(mat, srcGeo, matrix = null)` |
| [`L22880`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22880) | `buildMeshes(parentGroup, tooltipKey = null, opts = {})` |
| [`L22907`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L22907) | `buildChunkedMeshes(parentGroup, tooltipKey = null, opts = {})` |
| [`L23313`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L23313) | `calcNorm(px, py, pz)` |
| [`L25315`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25315) | `makeShipyardEnvMat(cacheKey, baseHex, rough, metal, fragExtraGLSL, options = {})` |
| [`L25995`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L25995) | `nextRandC()` |
| [`L26751`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L26751) | `nextRandVar()` |
| [`L27999`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L27999) | `addAquaWater(geo, px, py, pz, rx = 0, quat = null)` |
| [`L28301`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28301) | `rotXY(cx, cy, lx, ly, yaw)` |
| [`L28305`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28305) | `addVillageSmoke(ox, oy, oz, pIdx)` |
| [`L28310`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28310) | `addMudbrickHouse(cx, cy, w, d, hWall, yaw, hasAwning, hasLadder, idx)` |
| [`L28720`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28720) | `addUrCourtyardHouse(cx, cy, w, d, h1, h2, yaw, awMat, hasOven, idx, targetBatch = cityBatch)` |
| [`L28754`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28754) | `addWingRoof(wx, wy, ww, wd, wh, addVigas)` |
| [`L28838`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28838) | `addUrInsula(cx, cy, totW, totD, cols, rows, yaw, seedOff, targetBatch = cityBatch)` |
| [`L28860`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28860) | `addUrCityGate(gx, gy, outYaw)` |
| [`L28928`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L28928) | `addWallSpan(x0, y0, x1, y1, hWall, thick, hasCrenels = true, useKitWall = false)` |
| [`L29303`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29303) | `pushRoadTri(ax, ay, az, au, av, bx, by, bz, bu, bv, cx, cy, cz, cu, cv)` |
| [`L29307`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29307) | `addFlagstoneRoad(pts, width, tier = 0)` |
| [`L29384`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29384) | `pushStonePlazaPad(cxP, cyP, wP, dP, nxP = 4, nyP = 4, zLift = 0.042)` |
| [`L29422`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29422) | `pushOrgRoadTri(ax, ay, az, au, av, af, bx, by, bz, bu, bv, bf, cx, cy, cz, cu, cv, cf)` |
| [`L29427`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29427) | `addOrganicRoad(pts, width, meanderAmp = 0.55)` |
| [`L29850`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29850) | `appendCarvedCanalRibbon(pts, halfW, startExt = 0.0, endExt = 0.0, zStart = zCanalW, zEnd = zCanalW, watPts...)` |
| [`L29851`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L29851) | `buildDensePath(srcPts)` |
| [`L30120`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30120) | `addRiverIntakeSluice(ix, iy, dirToLandX, zWat, spanHalf = 3.3)` |
| [`L30254`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30254) | `addMagurBoatSlot(hasLogs, x, y, z, yawZ, boatInfo)` |
| [`L30372`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30372) | `addCanalArchBridge(bx, by, yaw, spanW = 10.6, roadW = 4.2)` |
| [`L30389`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30389) | `addTimberJetty(jx, jy, yaw, len = 10.5, zWater = 0.80)` |
| [`L30407`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30407) | `addGrainSilo(sx, sy, rad = 2.35, h = 4.4)` |
| [`L30416`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30416) | `addMudhifHut(mx, my, yaw, len = 7.2, wid = 3.8)` |
| [`L30435`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30435) | `addTownKiln(kx, ky, smokeIdx)` |
| [`L30577`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30577) | `evalRegionalRoadDist(px, py)` |
| [`L30589`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30589) | `isSafeAgriSpot(wx, wy, minRoadDist = 5.0)` |
| [`L30681`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30681) | `addUprightStrawRick(fx, fy, fIdx, withThreshFloor)` |
| [`L30717`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30717) | `addFieldShelter(sx, sy, yaw)` |
| [`L30831`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L30831) | `nextRandCrop()` |
| [`L31231`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31231) | `addCanalWeir(wx, wy, yaw, spanW = 6.4, zWater = 0.82)` |
| [`L31645`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31645) | `isInUrCityOrSuburb(x, y, pad = 0.0)` |
| [`L31653`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L31653) | `isShipyardWorkZone(x, y, pad = 0.0, forTrees = false)` |
| [`L32001`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32001) | `nextRandG()` |
| [`L32071`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32071) | `nextRandS()` |
| [`L32286`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32286) | `nextRandSt()` |
| [`L32402`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L32402) | `nextRandT()` |
| [`L33687`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33687) | `_loadSharedBotanyTextures()` |
| [`L33779`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33779) | `_prepTexForBotany(tex, isColor, repeatWrap)` |
| [`L33795`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33795) | `_adaptBotanyMaterial(species, srcMat, isFol, sharedTex, opts = {})` |
| [`L33874`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L33874) | `_extractSpeciesPack(species, glbScene, sharedTex, opts = {})` |
| [`L35093`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35093) | `_createUnifiedWorldTrimMaterial(srcMat, opts = {})` |
| [`L35293`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35293) | `_createCityTrimMaterial(srcMat, isRoad = false)` |
| [`L35297`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L35297) | `_openCityGateDoorsGeometry(geo)` |
| [`L36096`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36096) | `_createShipyardTrimMaterial(srcMat, isHot = false)` |
| [`L36594`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36594) | `_prepCharTex(tx, isColor)` |
| [`L36610`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36610) | `_loadLinearTex(url)` |
| [`L36618`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36618) | `_prepareCharacterGeo(obj, invRoot, rotX)` |
| [`L36662`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36662) | `_buildHeroLOD(figData, mat, tooltipKey, castShadowLod0 = true)` |
| [`L36684`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36684) | `_pickCitizenTypeForDryWorker(wp, idx)` |
| [`L36705`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36705) | `_pickCitizenTypeForWalker(cw, idx)` |
| [`L36727`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L36727) | `_mountAraratCharactersFromCache()` |
| [`L38898`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38898) | `nextRandSp()` |
| [`L38974`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L38974) | `nextRandSap()` |
| [`L41333`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41333) | `getDeviceClass()` |
| [`L41345`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41345) | `detectInitialTier()` |
| [`L41377`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41377) | `resolveTierFromMode(pMode)` |
| [`L41387`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41387) | `applyTier(tierIdx, force = false)` |
| [`L41462`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41462) | `resetGovernorClock()` |
| [`L41471`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41471) | `tickGovernor(nowMs)` |
| [`L41538`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41538) | `getCurrentSpec()` |
| [`L41542`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41542) | `setProfileMode(modeStr)` |
| [`L41554`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41554) | `init()` |
| [`L41562`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41562) | `restoreStandardVisibilities()` |
| [`L41608`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41608) | `updateExteriorPortalCulling(cam)` |
| [`L41764`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41764) | `updateLegendMode(mode)` |
| [`L41908`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L41908) | `updateScenarioDescription(scenName)` |
| [`L42217`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42217) | `translateGUI(lang)` |
| [`L42248`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42248) | `translateDOM(lang)` |
| [`L42476`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42476) | `showExpeditionBriefing()` |
| [`L42483`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42483) | `hideExpeditionBriefing()` |
| [`L42490`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42490) | `selectAppModeAndStart(mode)` |
| [`L42554`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42554) | `toggleLabExpeditionMode()` |
| [`L42563`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42563) | `reopenOnboardingModal(directBriefing = false)` |
| [`L42570`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42570) | `toggleLanguage(forceLang)` |
| [`L42778`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42778) | `getBadgirPairStationsX(count)` |
| [`L42786`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42786) | `updateBucketMeshGeometry(bucket)` |
| [`L42820`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42820) | `addPath(fn, pathType)` |
| [`L42842`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L42842) | `bezier3(p0, p1, p2, p3, u)` |
| [`L43179`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43179) | `updateZoharAndBadgirGeometry()` |
| [`L43434`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43434) | `computeBadgirMassTons()` |
| [`L43467`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43467) | `resetWaveAndShipState()` |
| [`L43723`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43723) | `triggerPauseEquilibriumRelax()` |
| [`L43727`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43727) | `markCustomPreset()` |
| [`L43784`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43784) | `syncQuickViewDock()` |
| [`L43800`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43800) | `toggleQuickAirflow()` |
| [`L43806`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43806) | `setQuickShader(modeStr)` |
| [`L43812`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43812) | `setQuickSlice(sliceStr)` |
| [`L43818`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43818) | `setQuickWall(wallStr)` |
| [`L43852`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43852) | `enterArkInterior()` |
| [`L43869`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43869) | `flyToInteriorDeck(deckKey)` |
| [`L43896`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L43896) | `updateInteriorNavHUD(forceNow = false)` |
| [`L44114`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44114) | `toggleHighlightTour()` |
| [`L44119`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44119) | `toggleFreeCameraMode(forceVal)` |
| [`L44304`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44304) | `applyPiersonMoskowitzWindSea(v_kmh)` |
| [`L44377`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44377) | `evaluateExpeditionLogistics(day, rain_mmh = 0.0, T_stall_C = 20.8, depth_m = 0.0, woodMoisturePct = 13.5, out ...)` |
| [`L44504`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44504) | `evaluateBiblicalChronicleState(day, instantSnap = false)` |
| [`L44905`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44905) | `syncChronicleUI()` |
| [`L44990`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L44990) | `toggleChronicleVoyage()` |
| [`L45008`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45008) | `startPreFloodBunkering()` |
| [`L45023`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45023) | `resetVoyageToLand()` |
| [`L45037`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45037) | `changeChronicleSpeed(val)` |
| [`L45042`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45042) | `scrubChronicleDay(val)` |
| [`L45085`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45085) | `computeRawICDNodeKN(wallIdx, lvlIdx, stIdx)` |
| [`L45131`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45131) | `computeScaledICDNodeKN(wallIdx, lvlIdx, stIdx, precomputedRawSum = null)` |
| [`L45147`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45147) | `generateICDMarkdownReport()` |
| [`L45225`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45225) | `translateMarkdownReportEN(md)` |
| [`L45245`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45245) | `openICDModal()` |
| [`L45258`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45258) | `refreshICDMarkdown()` |
| [`L45271`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45271) | `closeICDModal()` |
| [`L45274`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45274) | `copyICDMarkdown()` |
| [`L45284`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45284) | `downloadICDMarkdown()` |
| [`L45297`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45297) | `getFixturePopularTooltip(key)` |
| [`L45912`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45912) | `renderActiveTooltipContent()` |
| [`L45929`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45929) | `showDynamicTooltip(source, key, clientX, clientY)` |
| [`L45939`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45939) | `positionSciTooltip(clientX, clientY)` |
| [`L45953`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45953) | `hideSciTooltip()` |
| [`L45985`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L45985) | `resolve3DFixtureTooltipKey(hitObj, localPt, instanceId = undefined)` |
| [`L46152`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46152) | `_syncHoverSkipSet()` |
| [`L46211`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46211) | `_collectHoverTargets(node, out)` |
| [`L46231`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46231) | `_raycastInstancedFast(obj, worldRay, bestLimitDist)` |
| [`L46286`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46286) | `_precomputeHoverBounds()` |
| [`L46305`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46305) | `perform3DRaycastInspect(clientX, clientY)` |
| [`L46548`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46548) | `computeUtilizationRGB(etaEC5, etaBruch, blinkState, outRGB)` |
| [`L46591`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46591) | `computeThermalRGB(tempC, outRGB)` |
| [`L46620`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46620) | `getBeaufortInfo(v_kmh)` |
| [`L46635`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46635) | `update3DLabel(mesh, domElem)` |
| [`L46648`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46648) | `getBarColor(etaEC5, etaBruch)` |
| [`L46655`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46655) | `computeHullSectionProperties(hasCrossBracing, hasHeavyPlanking, hasSwelling, tempInteriorC, effWaveHalfLen_m)` |
| [`L46810`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46810) | `evalWebES(z_upper)` |
| [`L46859`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46859) | `evalESRatio(z_val)` |
| [`L46920`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46920) | `evaluateOceanWave(x_ship, y_ship, k, k_x, k_y, halfH, phi_rad, omega, depth, waveModel, out)` |
| [`L46975`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46975) | `getStationEffectiveKNPerMeter(stIdx)` |
| [`L46996`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L46996) | `evaluateICDWeightPerMeterMN(xs, totalWeightMN, payloadFrac)` |
| [`L47006`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47006) | `writeVolumeQuad(posArr, colArr, quadIdx, xA, yA, zTopA, rA, gA, bA, xB, yB, zTopB, rB, gB, bB, zFl...)` |
| [`L47021`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47021) | `writeFilmQuad(posArr, normArr, colArr, quadIdx, x0, y0, zBot0, zTop0, x1, y1, zBot1, zTop1, nx, ...)` |
| [`L47041`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47041) | `initOceanWaveWorker()` |
| [`L47047`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47047) | `evaluateExactHydrostatics(M_akt_t, V_ext_keels_m3, h_ext_keel_m, out = _maritimeScratch, rho_sea_override = ...)` |
| [`L47066`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47066) | `evaluateTransverseWaveFKFactor(k_y, B = B_SHIP)` |
| [`L47073`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47073) | `evaluateStripAddedMassAndSlam(subDraft, depth, geomSubDraft, draftBB_clean, draftSB_clean, vUpMid, vUpBB, vUpSB,...)` |
| [`L47104`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47104) | `stepSemiImplicitHeavePitch(heaveZ, heaveVel, heaveAcc, M11, C11, K11, pitchRad, pitchVel, pitchAcc, M22, C22,...)` |
| [`L47130`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47130) | `evaluateMetabolicHeatResponse(T_stall_C)` |
| [`L47140`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47140) | `evaluateBarnPhysiologyAndGasBalance(T_mean_C, RH_pct, T_bilge_C, Q_solar_roof_kW, Q_bio_total_kW, steamRate_kgh, V_dot...)` |
| [`L47247`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47247) | `evaluateAstronomyAndPsychrometrics(timeOfDay, latitude, cloudCover, extHumidity, precipIntensity, tAir, tWater, airPr...)` |
| [`L47362`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47362) | `evaluateCharnockWindAndSolAir(v_wind_10_kmh, H_wave, T_mean, badgirHeight, mu_wind_rad, rho_air, M_akt_t, GM_tra...)` |
| [`L47454`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47454) | `evaluateMassAndStabilityBalance(payloadPct, precipIntensity, dynRollRad, oxenBioEff, timeOfDay, out = _massStabScr...)` |
| [`L47637`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47637) | `evaluateThermalNetworkAndVentilation(T_current_C, prevRelHumidity, P_goepel_W, payloadFrac, waterDepth_m, T_mean, freeb...)` |
| [`L47757`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47757) | `evalStallHeatBalanceResidual(T_cand)` |
| [`L47999`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L47999) | `evaluateDAlembertStripDynamics(k, k_x, k_y, halfH, phi_rad, omega, depth, wModel, mu_rad, T_mean, KG_height, M_ak...)` |
| [`L48286`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48286) | `evaluateRollAndSurgeSwayDynamics(dynamicMotion, autoPlay, dt_phys, halfH, depth, T_mean, BM_radius, KG_height, GM_t...)` |
| [`L48484`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48484) | `evaluateSideGateHydrostatics(gateMode, isSideGateOpen, zWaterAtGate, T_mean, dynHeaveZ, dynPitchRad, dynRollRad...)` |
| [`L48610`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48610) | `evaluateInternalFixturesMechanics(payloadFrac, oxenPresence, oxenBioEfficiency, H_wave, dynRollRad, dynPitchRad, dyn...)` |
| [`L48625`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L48625) | `evalLocalG(x_m, y_m)` |
| [`L49105`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49105) | `evaluateHullHotspotsAndLUTs(payloadFrac, M_nutz_akt, m_roof_dyn, M_rain_roof_t, M_rain_soak_t, h_bilge_eff_m, ...)` |
| [`L49397`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49397) | `evaluateFatigueAndHotspotEC5(fatigueEnabled, chronicleActive, autoPlay, dt_phys, eqHoursStep, H_wave, omega, ma...)` |
| [`L49544`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L49544) | `evaluate3DFieldPointMechanicsAndThermal(meta, isBadgirPart, isRoofPart, ctx = _shaderFrameCtx, out = _fieldPointScratch)` |
| [`L50011`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L50011) | `evaluateVertexBufferColors(metaList, targetColArr, isBadgirPart, isRoofPart = false, ctx = _shaderFrameCtx)` |
| [`L50116`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L50116) | `evaluateEC5AndNorris(sigma_glob, sigma_loc_bend, sigma_90_trans, tau_xy, matObj, isScarfLoc, d_member_m...)` |
| [`L50710`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L50710) | `_initSSCS()` |
| [`L50875`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L50875) | `_resizeSSCS()` |
| [`L50887`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L50887) | `_isSSCSNearScene()` |
| [`L50907`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L50907) | `_runSSCSContactPass()` |
| [`L51099`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L51099) | `_compositeSSCSContactPass()` |
| [`L51109`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L51109) | `animate(isSingleTestStep = false)` |
| [`L52572`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52572) | `syncMobileViewportAndPerf(isInit = false)` |
| [`L52834`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52834) | `runArcheUnitTests()` |
| [`L52844`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52844) | `assertTest(suite, name, condition, detailStr)` |
| [`L54160`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L54160) | `openUnitTestModal(e)` |
| [`L54292`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L54292) | `_setBootProgressUI(pct, stageIdx, textDE, textEN)` |
| [`L54311`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L54311) | `_nextFrameYield()` |
| [`L54318`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L54318) | `_withTimeout(promise, ms, fallbackVal = false)` |
| [`L54331`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L54331) | `_computeMaterialProgramSig(obj, mat)` |
| [`L54359`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L54359) | `prewarmSimulationShaders(onProgress)` |
| [`L54733`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L54733) | `startArcheSimulationCleanly()` |


---

## 6. Vollständiges Unit-Test-Kataster (T01 bis T101)

> Ausgeführt durch `runArcheUnitTests()` (ab Zeile ~27436).  
> **Gesamt: 101 Tests** — 100% abgedeckt.

| ID | Zeile | Test-Suite | Test-Bezeichnung |
|:--:|:-----:|:-----------|:-----------------|
| **T01** | [`L52880`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52880) | 1. Ellen-Kanon, EN 338 & Clean Architecture | Biblische Hauptabmessungen (300 × 50 × 30 Ellen) |
| **T02** | [`L52885`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52885) | 1. Ellen-Kanon, EN 338 & Clean Architecture | 6–5–4–3-Handbreiten-Normquerschnitte (Glatte Handbreiten ohne cm-Rundung) |
| **T03** | [`L52890`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52890) | 1. Ellen-Kanon, EN 338 & Clean Architecture | EN 338 Fraktilmodul E_0,05 (Laubholz 0.84 vs. Nadelholz 0.67) |
| **T04** | [`L52896`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52896) | 1. Ellen-Kanon, EN 338 & Clean Architecture | EC5 Bemessungswerte f_d = f_k * k_mod / γ_M (NKL 3) |
| **T05** | [`L52900`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52900) | 1. Ellen-Kanon, EN 338 & Clean Architecture | 300-Knoten-ICD-Kataster Vollständigkeit & Symmetrie |
| **T06** | [`L52910`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52910) | 1. Ellen-Kanon, EN 338 & Clean Architecture | Glatte Ellen- & Handbreiten-Konsistenz (0,000 mm Zentimeter-Rundungsabweichung) |
| **T07** | [`L52921`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52921) | 1. Ellen-Kanon, EN 338 & Clean Architecture | Clean-Architecture-Registry (Arche.Groups & Arche.Materials), Basalt-Kombüse S7, Svalbard-Zeer & 0-ms-Schnittebene |
| **T08** | [`L52931`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52931) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Archimedisches Gleichgewicht T = (V_disp - V_Kiele) / (L*B*C_B) |
| **T09** | [`L52938`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52938) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Volumetrische Sensitivität V × ρ_EN338 (Sohle 5,0 Hände -> 6,5 Hände) |
| **T10** | [`L52942`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52942) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Metazentrische Anfangsstabilität GM_eff > 4.0 m |
| **T11** | [`L52946`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52946) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Freie-Oberflächen-Unterdrückung durch 7.500 Einzelfässer |
| **T12** | [`L52950`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52950) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | 3 Äußere Eichenkiele (Strandungs-Aufstandsfläche ≥ 350 m²) |
| **T13** | [`L52956`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52956) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Exakter Steiner-Formschwerpunkt KB & BM inkl. 3 Außenkiele |
| **T14** | [`L52968`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52968) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | D1-Fass-Wechselballast senkt KG, erhöht Tiefgang T & aufrichtendes Moment M·GM |
| **T15** | [`L52975`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52975) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Manning-Strickler-Regenwasseraufstau & Bilgenzulauf bei 1.200 mm/h Monsun |
| **T16** | [`L52981`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52981) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Kreiszylinder-Sehnenbreite b(h) = 2·√(R²-(h-R)²) maximiert |ΔGM| bei 50% Füllung |
| **T17** | [`L52987`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L52987) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | Flacher Bilgensumpf Pocket-Effekt dämpft freie Oberfläche bei starker Krängung |
| **T18** | [`L53008`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53008) | 2. Hydrostatik, Massenbilanz & Schwimmstabilität | 3D-Fass-Inventur (7.920 echte 8-Hände-Fässer) & 0 % Kollision (Silos, Schotttüren S1/14, Bâdgir-Schächte & Schnecken S4/11) |
| **T19** | [`L53017`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53017) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Miche-Flachwasser-Brecherlimit (H=20m bei d=12m begrenzt) |
| **T20** | [`L53024`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53024) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Stokes 3. Ordnung Kamm-Aufsteilung (η_Stokes > η_Sinus bei θ=0) |
| **T21** | [`L53030`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53030) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Wendel/Kim-Flachwasser-Quetschströmung (m'_add,flach > m'_add,tief) |
| **T22** | [`L53036`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53036) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Wagner/Ochi-Motter Keilslamming (Deadrise-Dämpfung bei φ=10° Krängung) |
| **T23** | [`L53042`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53042) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Analytischer Quer-Beugungsfaktor κ_trans(k_y*B) in Lang- vs. Kurzwelle |
| **T24** | [`L53048`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53048) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Unbedingte Stabilität des semi-impliziten Winkler-Felskontakt-Integrators |
| **T25** | [`L53055`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53055) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Nichtlineare Wall-Sided-Stabilität GZ(φ) > GM·sin(φ) bei φ = 15° |
| **T26** | [`L53066`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53066) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Ikeda-Kimmwirbeldämpfung B44_ikeda (Mittelkiel Y=0 + 2 Kimmkiele Y=±17.5 E.) |
| **T27** | [`L53070`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53070) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Vollständiger 6-DOF Roll-Trägheitstensor I_xx,tot (Struktur + ICD-Ladung + Added Mass) |
| **T28** | [`L53078`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53078) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | 2D-Beugungs-Surge (Auslöschung sinc(k_x·L/2) = 0 bei λ = L = 140 m vs. Langwelle) |
| **T29** | [`L53083`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53083) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Bodenkontakt-Arretierung (groundLock = 0 sperrt Surge/Sway bei Strandung) |
| **T30** | [`L53087`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53087) | 3. Wellenkinematik & 6-DOF-Hydrodynamik | Exakte Einzelpositionen (15 Längsgurte, 45 Stützen & 8 Bâdgire @ Y=±4.18m) in I_xx |
| **T31** | [`L53098`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53098) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Exakter Querkraft-Abschluss V_z(0) = 0 & V_z(140m) = 0 MN |
| **T32** | [`L53102`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53102) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Exakter Biegemoment-Abschluss M_y(0) = 0 & M_y(140m) = 0 MNm |
| **T33** | [`L53106`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53106) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Elastische 2-Knoten-Whipping-Eigenfrequenz f_1 im Zielband |
| **T34** | [`L53112`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53112) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | EC5 Anhang B (Möhler) — Wurzelknie erhöhen γ_mean & I_y,eff |
| **T35** | [`L53120`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53120) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | EC5 Gl. (6.17) — Exakt 100.0% bei σ_t,0,d = η_Schäft * f_t,0,d |
| **T36** | [`L53129`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53129) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | EC5 Gl. (6.19) — Quadratische Druck-Biege-Interaktion (u_c² + u_m) |
| **T37** | [`L53135`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53135) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | EC5 Gl. (6.23) — Biegeknicken (λ_rel > 0.30 -> k_c < 1.0 erhöht Ausnutzung) |
| **T38** | [`L53141`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53141) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | EC5 Gl. (3.1) — Höhenbeiwert k_h = (150/h)^0.2 für h < 150 mm |
| **T39** | [`L53147`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53147) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | 2D-Norris — Biaxiale Zug-Querdruck-Verschärfung (-u_0*u_90 > 0) |
| **T40** | [`L53151`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53151) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Johansen-Dübeltragfähigkeit (EC5 Gl. 8.6 & B.10) & Gustafsson k_v |
| **T41** | [`L53158`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53158) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Headless 2×2-D'Alembert-Löser schließt V_z(L), M_y(L) & M_t(L) exakt auf Null |
| **T42** | [`L53166`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53166) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | 3-Kiele-Winkler-Bodenkontakt erzeugt aufrichtendes Rollmoment (Y = ±17.5 E.) |
| **T43** | [`L53175`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53175) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Biaxiale Schrägbiegung (M_z), Vlasov-Wölbkrafttorsion & Racking-Schub in der 15×4-Hotspot-Suche |
| **T44** | [`L53186`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53186) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | 300-Knoten-Querdruck-LUT — 45 Eichen-Königsstützen senken Schwellen-Querdruck |σ_c,90| um >30% |
| **T45** | [`L53192`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53192) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | EC5 Gl. (6.15) Schub-Torsions-Interaktion, Gl. (B.10) Johansen-Dübel & Strandungspressung p_Strand |
| **T46** | [`L53204`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53204) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Kimmkanten-Rahmeneinspannung (L-Wurzelknie leiten Sohlenmoment in untere Bordwand ein) |
| **T47** | [`L53217`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53217) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Vierendeel-Rahmenbiegung & Eichen-Blockzargen-Entlastung an den 201 Schotttüren |
| **T48** | [`L53225`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53225) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | 2D-Zwischendeck-Durchlaufträgerbiegung σ_m = q·l²/(10·W) skaliert mit ICD-Knotenlast |
| **T49** | [`L53236`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53236) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Zohar-Ellen-Ausdehnung (300×50 E. vs. 260×21,5 E.) koppelt konsistent in Dachmasse & Vlasov-Torsion |
| **T50** | [`L53248`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53248) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Geschlossener Waben-Schott-Silo (I_y,Möhler > 400 m⁴, 0 Türen in S3/6/9/12 & 4:1 Schott-Widerstandsmoment) |
| **T51** | [`L53258`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53258) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | 720 Eichen-Wurzelknie (fixTag=5: Kimm-Wasserdruck nur außen, Norm-EC5 < 65% & Bruch-Stopp-Kopplung aktiv) |
| **T52** | [`L53267`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53267) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Hydrostatische Querquetschung (Querschott-Knicken), Dübel-Wechsellast-Verschleiß (K_ser) & Feuchte-Schüsselung (σ_cup,90) |
| **T53** | [`L53307`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53307) | 4. D'Alembert-Streifenkern, Möhler-Verbund & EC5-Rumpfstatik | Gen 8,1 Großer Gott-Wind (175 km/h Orkan, H=11,8m, 55° Schrägsee) — Innenschotten bruchsicher über 360° Phase |
| **T54** | [`L53352`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53352) | 5. 371-Tage-Chronik, Ermüdung & Instandhaltung | 371-Tage-Chronik (Kap. 14/15: Tag -20 leer -> Tag 20 Monsun -> Tag 146,5 Gott-Wind -> Tag 150 Grundsitz -> Tag 298 Ovoli -> Tag 371) |
| **T55** | [`L53357`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53357) | 5. 371-Tage-Chronik, Ermüdung & Instandhaltung | Palmgren-Miner-Wöhler-Akkumulation & logarithmische Madison-Dauerstandkurve k_mod(t) |
| **T56** | [`L53362`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53362) | 5. 371-Tage-Chronik, Ermüdung & Instandhaltung | Besatzungs-Wartung (Nachkeilen der 80.000 Hartholzdübel & Nachpechen in ruhiger Dünung) |
| **T57** | [`L53370`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53370) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Janssen-Silomechanik — Exakte Massenerhaltung (Wand + Sattel = 2.200 t) |
| **T58** | [`L53374`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53374) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Euler-Eytelwein-Seiltrieb (Paternoster F_Last > F_Leer, Ausnutzung < 100%) |
| **T59** | [`L53378`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53378) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | 3-Bahnen-Verteiler-Hub — Großtier-Rampen-Trittsicherheit S_Tritt > 1.50 |
| **T60** | [`L53382`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53382) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Alle 14 Einbauten-Systeme frei von NaN & im EC5-Bemessungsrahmen |
| **T61** | [`L53388`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53388) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | 9×8-Ellen-Seitentor Hydrostatik (F_w = ρ·g·A_w·h_c) & 6-Hände-Blockzargen-Schutz |
| **T62** | [`L53393`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53393) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Torricelli-Flutungs-Hydraulik Q_flood bei offenem 9×8-Ellen-Seitentor (4,0 Hände Bordwand) |
| **T63** | [`L53398`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53398) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Ortsaufgelöste Janssen-Silodruck-Erhöhung (Außenblöcke S3/S12 |Δx|=45m > Innen S6/S9 |Δx|=15m) |
| **T64** | [`L53402`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53402) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Vor-/Achterschiff-Asymmetrie der beiden Paternoster & Göpel (S4 @ X=35m vs. S11 @ X=105m) |
| **T65** | [`L53407`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53407) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Großtier-Rampen-Trittsicherheit S_Tritt(θ,φ) & 5,4-t-Basalt-Kombüsen (max g_eff S7/S13) |
| **T66** | [`L53417`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53417) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | 3D-Janssen-Tiefenprofil in den 224 Silowänden & 60°-Trichtersattel (Sattel > Fuß > Kopf) |
| **T67** | [`L53430`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53430) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Holz-Stein-Tribologie (6:1 Stockgetriebe im Ellen-Maß) & 12,3-kWh-Schichtfahrplan (5,5 h/Tag, Kap. 9.4–9.5) |
| **T68** | [`L53446`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53446) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | 3-Zweig-Kupplungsgetriebe (Exakte Drehmoment-Bilanz ΣM_Zweige = M_Göpel & Lastabwurf beim Auskuppeln) |
| **T69** | [`L53451`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53451) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Saint-Venant-Wellentorsion τ_t = 16·M_t/(π·D³) (Königswelle D=6H vs. 6:1-Querwellen D=2H) |
| **T70** | [`L53456`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53456) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | Synchronisierte Deck-3-Einbauten (Basalt-Kombüse S7, Svalbard-Zeer S8 & Zimmermannswerkstatt |WERK|) |
| **T71** | [`L53464`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53464) | 6. Holz-Stein-Maschinenbau, Silos & Einbauten | 3D-Kraftfluss-Overlay (6 Zugkraft-Vektoren, 4 Drehmoment-Stromlinien & 3D-Schneckenwasserstrom) |
| **T72** | [`L53471`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53471) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Psychrometrie & Svalbard-Kühlung (T_FK <= T_Saatgut <= T_Stall) |
| **T73** | [`L53475`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53475) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Rinder-Physiologie (Boviner THI < 72 & DIN 18910 CO₂ < 3.000 ppm im Normfall) |
| **T74** | [`L53482`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53482) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | CIGR-Thermogenese (<8°C) vs. NRC-Anorexie-Drosselung (>26°C) |
| **T75** | [`L53488`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53488) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Ammoniak-Urease (NH₃ < 20 ppm) & Seewasser-Schwallspülung + CH₄-UEG |
| **T76** | [`L53492`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53492) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Vertikale 3-Decks-Temperaturschichtung (T_D1 < T_D2 < T_D3) |
| **T77** | [`L53497`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53497) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Bovine Kerntemperatur T_core (Hyperthermie bei Hitzestau) & Trinkwasserbedarf |
| **T78** | [`L53503`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53503) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | DIN-18910-Schadgas-Anstieg bei geschlossenen Schotttüren & Schwachlüftung |
| **T79** | [`L53509`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53509) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Sonnenbahn (Mittagszenit α = 90° - |φ - δ| = 68° vs. Mitternacht α < 0°) |
| **T80** | [`L53515`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53515) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Dalton-Gasgesetz & Magnus-Taupunkt (Feuchte Luft ist leichter als trockene Luft!) |
| **T81** | [`L53521`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53521) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Charnock-Meeresrauigkeit z_0 & logarithmisches Prandtl-Windprofil v_First > v_10 > v_Mid |
| **T82** | [`L53527`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53527) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Sol-Air-Dachbilanz — Solar-Aufheizung am Tag vs. Stefan-Boltzmann-Unterkühlung nachts |
| **T83** | [`L53532`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53532) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Psychrometrische Monsun-Dachkühlung (T_sol-air nähert sich bei Starkregen T_precip an) |
| **T84** | [`L53541`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53541) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Borda-Carnot-Schotttüren — Geschlossene Türen drosseln Lüftung & heizen Stall auf |
| **T85** | [`L53547`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53547) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | 14-Schritt-Bisektion & 2. Hauptsatz im Bilgen-Wärmetauscher (12°C vs. 34°C Meer) |
| **T86** | [`L53558`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53558) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Bâdgir-Innenschächte verhindern Dach-Kurzschluss & senken Turmfuß-Biegung um >60% |
| **T87** | [`L53571`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53571) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | 3D-Infrarot-Thermografie (T_Unterwasserwand < T_Innenstall < T_Sol-Air-Dach) |
| **T88** | [`L53580`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53580) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Bewegliche 3D-Sturmklappen an Zohar & Bâdgiren (Luv/Lee-Automatik im 1-Draw-Call InstancedMesh) |
| **T89** | [`L53587`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53587) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Dynamische Sturmklappen-Aerodynamik (α_Luv schließt im Orkan -> c_w sinkt & 94% Schlagregen-Abweisung) |
| **T90** | [`L53595`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53595) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | O2-Bilanz (RQ=0.85), H2S-Sulfat-Faulgas (Pumpen EIN vs. AUS), Erdregister & Silo-Taupunktschutz (> +3 K) |
| **T91** | [`L53611`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53611) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Manuelle Steuerung von Regentemperatur (T_Regen) & Bilgenwassertemperatur (T_Bilge) im Wärmenetzwerk |
| **T92** | [`L53636`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53636) | 7. Meteorologie, Bauphysik & Veterinär-Physiologie | Wetter-Pakete A–D, 14 Szenario-Presets & 3D-Mikroklima-API (EC1-Schneelast, 3000m Ararat, ρ_See, Kombüse vs. Svalbard) |
| **T93** | [`L53648`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53648) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | Tierbestand (2.800 Gattungen | 6.350 Tiere | 1.100 t) & 3-m³-Svalbard-Tresor (40 Pithoi + 12 Zeer-Kühlröhren, Kap. 12.5) |
| **T94** | [`L53677`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53677) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | 3D-Fauna-Engine (6.350 Tiere, 8 Groß-Volieren vor Silos, Bâdgir-Öffnungen D1–D3 & Rinnen nur im Hauptgang) |
| **T95** | [`L53714`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53714) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | Zweisprachige DE/EN-Tooltip-Engine (100% Abdeckung für alle Dashboard-Keys, 67 GUI-Regler & 15 Szenarien) |
| **T96** | [`L53737`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53737) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | Modus-sensitiver 3D-Hover (Museum=Funktion | EC5=Kraft & % | Thermo=°C) & Auto-Gerätesprache (DE/EN) |
| **T97** | [`L53748`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53748) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | Numerische Stabilität — 0 NaN/Infinity-Werte im gesamten liveState |
| **T98** | [`L53809`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53809) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | 3D-Luftstrom-Netz (Arche.Groups.airflow3D ≥ 1500 Vertices), Zweikammer-Geschwindigkeitsfeld (Bâdgir Fall/Kamin, Atrium, Silo), CH4-Schichtung & Windwinkel-Kopplung (μ=90° > μ=0°) |
| **T99** | [`L53829`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53829) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | macOS Safari/Metal-GLSL-Konformität, Auto-FPS-Governor (≥ 30 FPS) & Mobile-UX |
| **T100** | [`L53911`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L53911) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | Vollständige GPU-Beschleunigung (GPU-Stokes-Ozean, Ballistischer GPU-Splash-Shader & 0-ms-GPU-Instanz-Clipping) |
| **T101** | [`L54127`](file:///C:/Users/Daniel Unger/Desktop/KI/Arche Buch/Arche Simulation 3.0.html#L54127) | 8. 3D-Fauna-Engine, Bilinguale UI & System-Stabilität | Bronzezeitlicher Werftplatz (Tag -7) & Ararat-Hochgebirgsmassiv (Tag 150–371) |

---
*Ende des generierten Index. Bei jeder Code-Modifikation `node index_arche.js` im Terminal ausführen!*
