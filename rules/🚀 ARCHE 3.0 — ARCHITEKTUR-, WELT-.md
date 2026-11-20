# 🚀 ARCHE 3.0 — GESAMT-BLUEPRINT (ENGINE, WELT, GRAFIK, LICHT, WETTER, BAU-CHRONOLOGIE, ANIMATION, PHYSIK & ÖKOSYSTEM)

> **Status:** Vollständiger Master-Blueprint (Stand: November 2026)  
> **Startzeitpunkt:** Erst nach sauberem **Freeze von ARCHE 2.0** (Arche Welle A–C + 28 Tierfamilien + 3D-Raumklang komplett & `101/101 PASS`).

---

## 1. Strategische Leitidee & Übergang ARCHE 2.0 → 3.0

1. **Sauberer Schnitt statt Monolith:**
   - ARCHE 2.0 (`Arche Simulation 3.0.html`, ~50.000+ Zeilen Single-File) wird als abgeschlossener, lauffähiger Meilenstein (inkl. WebGL1-Support für Altgeräte) eingefroren.
   - Alle Konstanten, First-Principles-Gleichungen, Welten, Maße und die **101 Unit-Tests (`T01–T101`)** werden in **7 verbindliche Übergabe-Spezifikationen** (`AGENTS.md` + `docs/01` bis `docs/06`) extrahiert.
   - Start in einem frischen, streng modularen Repository **`arche-3.0/`**.
2. **100 % Wiederverwendung aller ARCHE-2.0-Blender-Assets:**
   - Sämtliche `.blend`-Master aus ARCHE 2.0 (53 MPFB-Menschen, Hero-Tempelbezirk, Werft, Botanik, Ararat, Arche-Module, 28 Tierfamilien) werden **1:1 übernommen**, im `LOD0` gezielt veredelt und per Batch-Pipeline nach **`4K KTX2` + `Meshopt`** re-exportiert.

---

## 2. Engine-, Render- & Entwickler-Architektur (`Babylon.js 9.x` + `Rust-Wasm`)

### 2.1 Kern-Stack (Hybrid-Powerhouse)
Statt Monate in Basisinfrastruktur (glTF-Loader, PBR/IBL, Safari-Treiberbugs, WebGL2-Fallback) zu investieren, kombinieren wir **Babylon.js 9.x (Apache-2.0)** mit unserem eigenen **Rust-Wasm-Simulationskern** und maßgeschneiderten **WGSL-Compute-Shadern**:

| Schicht | Technologie in ARCHE 3.0 | Konkreter Nutzen |
|---|---|---|
| **3D-Engine & Renderer** | **Babylon.js 9.x (`@babylonjs/core`, Apache-2.0)** — **WebGPU (100 % native WGSL-Core-Shader)** + automatischer **WebGL2-Fallback** | Läuft auf ~89,5 % WebGPU-Browsern (inkl. Chrome, Edge, Firefox & Safari 26 / iPadOS 26) und fällt nahtlos auf WebGL2 zurück; volle Tree-Shaking-Modularität |
| **Beleuchtung & Atmosphäre** | **Clustered Lighting**, **Area Lights**, **Volumetric Fog**, **OpenPBR** & **Physically Based Atmosphere** | Hunderte dynamische Lichter gleichzeitig (Glimmer-Laternen D1–D3, Ziggurat-Feuerschalen, Stadttor-Fackeln, *Tannur*-Öfen) + echte **Zôhar-Lichtkegel** bei 60 FPS |
| **Reflexionen, AO & Schatten** | **Planar `MirrorTexture` + Hi-Z `SSR2` + Dynamic IBL** \| **`ORM` + `SSAO2` + Kontakt-AO** \| **4-Kaskaden-CSM + `SSCS` + IBL/Terrain-Shadows** *(s. 2.4)* | Spiegelklare Abzu-Teiche, glänzendes nasses Pech/Pfützen, fest verankerte Füße/Hufe und messerscharfe Schatten bis 12 km (`~3,2 ms` gesamt!) |
| **Draw-Call- & Welt-Skalierung** | **Snapshot Rendering (WebGPU Render Bundles)**, **Frame Graph**, **Thin Instances**, **Vertex Animation Textures (VAT)**, **GPU Mesh Picking** & **Large World Rendering** | Minimale CPU-Last für 2.500 Häuser in Schuruppak, ~12.000 Einzelholzbalken, 7.920 Fässer, 6.350 Tiere & 500 laufende Bürger; präzise 12-km-Welt ohne Float-Jitter |
| **Temporal Upscaling** | Eigener **`WGSL`-Compute-Pass im Frame Graph („TSR-Lite + FSR-Tricks“)** *(s. 2.2)* | Gestochen scharfe `1080p/4K`-Optik bei `67–75 %` interner Auflösung → **+40–70 % GPU-Headroom** auf GTX 1070, iPad & Mobile |
| **Physik, Statik & Welt-Logik** | **Rust → WebAssembly (`v128 SIMD` + `SharedArrayBuffer`)** | 10–30× schneller als JS; 6-DOF, Stokes-3, D'Alembert/Whipping, EC5-γ-Verfahren, Janssen-Silos, 5-Gas-Klima, globales Klima-, Smart-Layout- & Crowd-System auf Worker-Threads |
| **Tone Mapping & Modi** | **AgX** (`TEXTURED`) vs. **`NoToneMapping`** (`EC5`/`THERMAL`/`COMFORT`) | Strikt unverfälschte Analysefarben & Arche-Farbschutz wie im ARCHE-2.0-Kanon |
| **Raumklang** | **Babylon.js Web Audio Engine** + prozedurale Web Audio Synthese + Raum-Okklusion | 0 Byte MP3s; dumpfes Holz-Knarzen & Tierdecks innen vs. Wind, Brandung & Marktplatz außen |

### 2.2 Temporal Upscaling in WGSL: Best-of-Both-Worlds (`TSR-Lite + FSR 2/3.1`)
Da FSR-3-Frame-Generation im Browser technisch ungeeignet ist (fehlende Low-Level-Swapchain, Input-Lag, iPad-VRAM), kombiniert ein schlanker eigener `WGSL`-Frame-Graph-Pass das Beste beider Verfahren:
1. **TSR-Kern (Bildruhe & Detailtreue):** Halton-2,3-Subpixel-Jitter, exakte Kamera- & Objekt-Motion-Vectors (6-DOF-Rumpf, Göpel, VAT-Charaktere), **Catmull-Rom-/Lanczos-History-Sampling** und **YCoCg Variance Clipping** → flimmerfreie Palmenwedel, Dattelrispen, Weintrauben, Seile & Holzdübel (glättet zudem `SSR2` & `SSAO2`!).
2. **FSR-2/3.1-Tricks (Wasser, Effekte & Schärfe):**
   - **Reactive Mask:** Markiert bewegte Ozeanwellen, Schaum, Regen, Blitze, Rauch, GPU-Partikel & Zôhar-Lichtstaub → **0 Ghosting**!
   - **RCAS (*Robust Contrast-Adaptive Sharpening*):** Ultraleichter Schärfe-Pass (~0,15 ms) für knackige Kanten.
3. **Skalierungs-Modi & Analyse-Reinheit:** `Nativ 100 %`, `Qualität 75 %`, `Ausgewogen 67 %`, `Performance 58 %`; in Analyse-Modi (`EC5`, `THERMAL`, `COMFORT`) standardmäßig **`100 % Nativ`**.

### 2.3 Rechner-Vorbereitung & Blender-4.x → Babylon.js-9.x-Pipeline
- **PC-Setup (~15 Min. beim Start von `arche-3.0/`):** `pnpm`/`npm` + **TypeScript** + **Vite** (inkl. `COOP/COEP`-Headern für `SharedArrayBuffer`) + **`rustup` / `wasm32-unknown-unknown` / `wasm-pack`** + **Khronos `KTX-Software` (`toktx`)** + **`gltf-transform` CLI** + aktueller NVIDIA-Treiber (GTX 1070).
- **Nahtlose Blender-Integration (100 % kompatibel zu `BLENDER_PIPELINE.md`):**
  * Standard **glTF 2.0 / `.glb`**-Exporter, **rechtshändiger Modus** in Babylon.js (keine Achs-Dreherei!), identisches **`ORM`-Packing** (AO/Roughness/Metallic) + `BaseColor (sRGB)` + `Normal (Linear)` + optionaler `Height`-Kanal für `< 18 m`-POM.
  * **Kompression:** **`KTX2`** spart 70–85 % VRAM (**Normalmaps zwingend in `UASTC`**, kein aggressives ETC1S!) + **`Meshopt` statt `Draco`** für blitzschnelle Ladezeiten; Live-Check per **Babylon Sandbox** & **Inspector v2**.

### 2.4 Mehrstufige Reflexions-, AO- & Schatten-Pipeline (`~3,2 ms` GPU-Gesamtbudget, 0 Hardware-RT!)

#### A) 3-Stufen-Reflexionen (`~1,2 ms` — ohne Hardware-Raytracing!)
1. **Planar Reflections (`MirrorTexture` @ Half-Res, `~0,4 ms`, `< 120 m`):** Für **Abzu-Tempelteiche & ruhigen Euphrat** — spiegelt Ziggurat, Feuerschalen, Palmen & Himmel vollständig (auch wenn der Turm oben aus dem Bildschirm ragt!), verzerrt durch die **2D-Shallow-Water-Normalmap** + physikalischen Schlick-Fresnel (schräg spiegelklar, senkrecht durchsichtig bis auf den Mosaikboden!).
2. **Hi-Z Screen-Space Reflections (`SSR2RenderingPipeline` @ Half-Res + TSR, `~0,7 ms` Desktop / IBL-Fallback auf Mobile):** Lässt **Regenpfützen** auf der Königsstraße, **nasses Kopher-Pech** im Sturm, **Zinnbronze**, **glasierte Lapislazuli-Ziegel** & **Ozeanwellen** realistisch glänzen; `TSR-Lite` entrauscht halbauflösendes SSR automatisch.
3. **Dynamische IBL / Lokale Reflection Probes (`~0,1 ms`):** Synchronisiert Außenlicht (Sonne, Gewitter, Blitze) auf `OpenPBR`-Materialien; **1–2 lokale Probes im Arche-Innenraum** liefern warmes Laternen- & Zôhar-Spiegellicht statt blauem Außenhimmel.

#### B) 3-Stufen-Ambient-Occlusion (`~0,5–0,7 ms`)
1. **Gebackene Mikro-AO im `ORM`-R-Kanal (`0,0 ms`):** Fugen, Fassreifen, Nischen & Wurzelknie direkt aus Blender Cycles.
2. **`SSAO2` (GTAO) @ Half-Res + Temporal Denoise (`TSR-Lite`, `~0,4–0,6 ms`):** Gibt engen Gassen in Schuruppak, 13 Querschotten, Fässern & Silos sattes Raumgewicht ohne Kriseln.
3. **Analytische Boden-Kontakt-AO (`~0,1 ms`):** Weicher Kontaktfleck unter laufenden Füßen, Sandalen, Hufen & Tierbäuchen (kein Schweben!).

#### C) 4-Band-Schatten-Architektur (`~1,5–2,0 ms`)
1. **Band 1 & 2 (`0–450 m`): Stabilisierte 4-Kaskaden-CSM (`PCF`/`PCSS` + Texel-Snapping):** Kaskade 0 (`0–18 m`, messerscharf für Menschen, Tiere, Balken, Seile) bis Kaskade 3 (`200–450 m`, Stadtviertel/Wälder; äußere Kaskaden nur alle 2–3 Frames aktualisiert → `-40 %` Kosten!).
2. **Band 3 (`0–28 m` Nahbereich): Screen-Space Contact Shadows (`SSCS`, `~0,4 ms`):** Fängt millimeterfeine Details ein (**Holzdübel, Weintrauben, Dattelrispen, Sandalenriemen, Falten & Hufe**).
3. **Band 4 (`450 m – 12 km` Fernhorizont): Terrain-Horizontschatten + Babylon `IBL Shadows`:** Kostenlose Gebirgs- und Wolkenschatten bis zum Ararat-Gipfel.
4. **Arche-Innenraum & Nachtfeuer:** Sonne schneidet über Kaskade 0 + **Volumetric Fog** durch den `1-Elle`-Zôhar (und abgedeckte Dachplanken Gen 8,13); hunderte Laternen/Fackeln laufen schattenfrei über **Clustered Lighting**, während nur **1–2 nahe Hero-Lichter** (z. B. Noahs Handlaterne / Altarfeuer) echte Nah-Schatten werfen.

---

## 3. Grafik-, Material-, Detail- & Animations-Architektur

### 3.1 Warum KEIN Gaussian Splatting (3DGS) für dynamische Welt-Assets — und die besseren AAA-Alternativen
3DGS in Babylon.js 9.x (`.SPZ`/`.SOG`) besitzt eingebackenes Licht, lässt sich nicht billig per Knochen/Wind animieren, sprengt durch Tiefensortierung das Mobile-Budget und wird unter `< 1 m` wolkig. *(Optionale Nische nur für statische Museums-Infoboxen echter Ausgrabungs-Scans!)* Stattdessen nutzen wir für maximale AAA-Qualität bei 60 FPS:

1. **🌴 Pflanzen- & Mikro-Botanik bis zu Dattelrispen & Weinstöcken (`KHR_materials_scatter` + `LOD0`-Fruchtcluster):**
   - **Blatt-Translucency (`KHR_materials_scatter`):** Sonnen- & Blitzlicht scheint physikalisch warm grün-golden durch Palmenwedel, Weinlaub, Schilf & Granatapfelblätter.
   - **Synchroner Vertex-Wind:** Stämme, Wedel, Weinranken, Getreide & Schilf wiegen sich im gemeinsamen Windvektor.
   - **Mikro-Artenvielfalt via `LOD0`-Fruchtcluster (`< 18–20 m`):** In Blender (`Geometry Nodes` + `Sapling` + `IvyGen`) erstellte botanische Module blenden im Nahbereich echte **Dattel-Fruchtstände unter Palmenkronen**, **gewundene Weinstöcke mit hängenden Traubenbüscheln an Holzspalieren**, **Granatäpfel, Feigen, Oliven** sowie Felder/Beete für **Gerste, Emmer, Sesam, Flachs/Lein, Linsen, Kichererbsen, Zwiebeln, Knoblauch, Papyrus & Schilf** ein — ab `> 20 m` verschmelzen die Beeren/Früchte kostenlos ins schlanke `LOD1`.
2. **🦁 Hohe Artenvielfalt & realistische Tierfelle (`2.800 Gattungen` im `~35–50 MB` VRAM-Budget):**
   - **~35 anatomische Blender-Familien-Rigs (`Rigify`)** + **Morph-Targets (Shape Keys)** für Hörner, Schnauzen, Ohren, Halslängen, Buckel & Proportionen + **`species_dna.json`**-Shader für Fellmuster (Streifen, Flecken, Rosetten), Gefiederschimmer & Größen.
   - **GPU „Shell-Texturing“ (`< 15 m` in WGSL):** Nahe Säugetiere (Löwen, Zugochsen, Bären, Wölfe, Schafe) erhalten **8–16 geschichtete Fell-Schalen** mit Haarwurzel-AO, **Kajiya-Kay-Rim-Glanz** und sanfter Bewegungsträgheit (`~0,4 ms`, ab `> 15 m` stufenlos 1 Schicht).
3. **🧔 Menschen-Haare & Bärte (`LOD0 < 12 m`):**
   - Mehrschichtige **anisotrope Hair-Cards** (aus Blender-Hair-Curves gebacken) mit seidigem Lichtglanz entlang der Strähnenrichtung unter Sonne, Fackeln und Laternen; nahtloser Übergang auf schlanke Meshes ab `LOD1`.
4. **👗 Dynamische Kleidung (0 % Haut-Clipping, `~0,05 ms` GPU-Zeit):**
   - **Stufe 1 (alle 300–600 aktiven Bürger): GPU-Vertex-Cloth via `Cloth_Mask`:** Schultern, Torso & Hüfte bleiben `0.0` (starr am Skelett = **garantiert 0 % Haut-Clipping**); nur freie Säume (Schärpen-Enden, Tunika-Unterkante, Kopftuch-Schleier, weite Ärmelränder) schwingen im Wind und Geh-Rhythmus.
   - **Stufe 2 (Noahs 8-köpfige Familie & nahe Heroes `< 12 m`): Leichte Rust-Wasm „Spring-Bones“:** 2–3 träge Knochenketten je Figur lassen Noahs langen Mantelzipfel, Gürtelbänder und Frauenschleier echt im Sturm auf Deck 3 & am Ararat wehen.
5. **🤖 KI + Blender Automatisierungs-Regeln (Power ohne „AI-Slop“ & VRAM-Crash):**
   - **Erlaubter Turbo:** KI schreibt **Blender-Python- & Geometry-Nodes-Skripte** (die z. B. 12–15 natürliche Weinstock-, Baum- oder Haus-Varianten mit perfekten LODs + `ORM` backen) und kuratiert die `species_dna.json` (2.800 Gattungen).
   - **Verboten:** Rohe „Text-to-3D“-Meshes (chaotische Topologie, zerfetzte UVs, 60k Tris) und tausende uninstanziierte Einzeldateien, die das sichere **`~3–4 GB` Browser-VRAM-Limit** (GTX 1070 / iPad) sprengen. Jedes Asset durchläuft weiterhin die knallharte **`visual-critic`-Prüfung**.
6. **🧱 Fassaden-Tiefe & Oberflächen-Plastizität (gegen „flache Tapeten-Wände“):**
   - **Smarte `LOD0`-Silhouetten (`+600–1.000 Tris/Haus` `< 35 m`):** Leicht angefaste, organisch gebrochene Lehmputz-Ecken (kein 90°-CAD-Würfel!), echte `10–15 cm` eingerückte Fenster-/Türnischen, Steinsockel & Ziegelsimse (ohne einzelne 3D-Ziegel zu modellieren!).
   - **Distanzbegrenztes Parallax Occlusion Mapping (`POM`, Babylon `useParallaxOcclusion`):** Nur im **`< 18 m`-Nahbereich** (Desktop) auf Ziegeln, Pflastersteinen, Königsstraße & Basalt über kompakten Height-Kanal.
   - **World-Space Putz- & Verwitterungs-Blend (`~0,15 ms`, `0` extra RAM):** Mischt glatten Kalk-/Lehmputz, abplatzende Stellen mit sichtbaren plankonvexen Ziegeln und dunkle aufsteigende Bodenfeuchte (`0–1,2 m`) → bricht jede Textur-Wiederholung über alle 2.500 Häuser; ab `LOD1` (`> 35 m`) automatisch wieder leicht.

### 3.2 Natürliche Bewegungs- & Motion-Capture-Pipeline (`MPFB + Mocap + Babylon VAT`)
Schluss mit dem steifen ARCHE-2.0-Vertex-Pendelgang („Stelzen-/Hampelmann-Lauf“ ohne Kniegelenke!):
1. **Echte Motion-Capture-Bibliotheken für alle 53 Menschen & ~35 Tierfamilien (100 % kostenlos & lizenzfrei):**
   - **Menschen (`MPFB2` + `Mixamo-Rig` / `ACCAD` / `CMU Mocap` / `Mesh2Motion`):** Nutzung des direkt in **MPFB2** integrierten Mixamo-Rig-Modus sowie Open-Source-Mocap-Datenbanken (`.bvh`/`.fbx` → Retargeting in Blender auf unsere MPFB-Figuren) für entspanntes Gehen (echtes Kniebeugen, Fuß-Abrollen, Hüftwiegen), Lastentragen, Zimmerer-Arbeit, Rudern, Priester-Gesten, Sitzen & ruhiges Stehen.
   - **Tiere (`Mesh2Motion` Open Source + `Rigify`):** Natürliche Gangarten (*Walk, Trot, Run, Graze, Drink, Rest, Flap/Glide*) für Vierbeiner, Zugochsen am Göpel & Vögel.
2. **Dual-Ausführung in Babylon.js 9.x (0 ms CPU-Last für Massen, volle Qualität für Heroes!):**
   - **Noahs 8-köpfige Familie & nahe Interaktions-Tiere:** Volles **glTF-Skelett-Animation-Blending** + **Spring-Bones**.
   - **300–600 Stadt-/Werft-Bürger & 6.350 Tiere:** Gebacken über den eingebauten **`VertexAnimationBaker` in `Vertex Animation Textures` (VAT)** → `Thin Instances` mit echtem Gelenk-Gang bei **`0,0 ms` CPU-Skinning-Kosten**!
3. **Strict Speed-to-Stride-Sync (0 „Moonwalking“):** Der Rust-Wasm-Crowd-Solver koppelt die Animationsfrequenz exakt an die reale Bodengeschwindigkeit (`v_real = schrittlaenge * frequenz`), inkl. Übergang in ruhige Stand-/Arbeitsposen beim Stehenbleiben.

---

## 4. Parametrisches Ingenieur- & Schiffbau-Labor

### 4.1 Historisches Ellen-Labor (5 antike Ellen im Live-Vergleich)
Voll-parametrischer Aufbau auf `ELLE_M` und `HANDBREITE_M`:

| Historische Elle | Kultur / Unterteilung | Maß | Faktor $\lambda$ | Rumpf `300 × 50 × 30` Ellen | Volumen ($\lambda^3$) |
|---|---|---|---|---|---|
| **Kurze hebräische Elle** (*Ammah*) | 6 Hände (24 Finger) | `44,5 cm` | `0,954` | `133,5 × 22,3 × 13,4 m` | −13,2 % |
| **ARCHE-Standard-Kanon** *(Default / 101 Tests)* | 6 Hände (`14/30 m`) | **`46,67 cm`** | **`1,000`** | **`140,0 × 23,3 × 14,0 m`** | ±0 % |
| **Gudea- / Altbabylonische Elle** (*Kùš*) | 30 Finger | `49,8 cm` | `1,067` | `149,4 × 24,9 × 14,9 m` | +21,5 % |
| **Sumerische Nippur-Elle** (*Kùš*, ~2650 v. Chr.) | 30 Finger (*Šu-si*) | `51,8 cm` | `1,110` | `155,4 × 25,9 × 15,5 m` | +36,8 % |
| **Ägyptische / Ezechiel-Königselle** | **7 Hände** (28 Finger) | `52,4 cm` | `1,123` | `157,2 × 26,2 × 15,7 m` | +41,6 % |

- **2 Vergleichs-Modi:** *Geometrisch proportional* (**Square-Cube-Law**: $\sigma_m \propto \lambda^1$, γ-Schlupf steigt überproportional, $f_1 \propto \lambda^{-1}$, konstante `1.100 t` Biomasse) vs. *echte 7-Handbreiten-Metrologie* (feste Handbreite `~7,78 cm` bei `52,4 cm`-Königselle → zeigt im EC5-Norris-Nachweis die physikalische Obergrenze des Großholzschiffbaus!).

### 4.2 Schiffbau-Vergleich: Zelluläre Schottenbauweise (*Kanon*) vs. Reine Schale vs. Skelettbauweise
Direkte physikalische & visuelle Umschaltung zwischen den drei großen historischen Holzschiffbau-Systemen:
1. **Zelluläre Schottenbauweise (*Cellular Bulkhead Construction* — ARCHE-Kanon!):**
   - **13 Querschotten** (mit 201 blockzargenversteiften Türen) + **2 Längsschotten** + **15 Kielschweine** + **45 Königsstützen** + **720 Wurzelknie** + **224 Silozellen** + **Decks D1–D3**, außen geschlossen über **verdübelte Außenplanken (80.000 Hartholzdübel)**.
   - **Statische Wirkung:** Steifer **Bredt/Vlasov-Kastenträger** + **Vierendeel-Rahmen** + hoher EC5-Verbundwirkungsgrad $\gamma$ + optimale Aufnahme der hydrostatischen Querquetschung → trägt `140 m` sicher durch den Auslegungs-Seegang!
2. **Reine Schalenbauweise ohne Schotten (*Pure Shell-First* — antikes Großboot hochskaliert):**
   - Kante-an-Kante verzapfte Planken ohne das innere 13×2-Schotten-Wabengitter → **bricht im EC5-Solver unter hydrostatischer Querquetschung und fehlender Torsionsaussteifung sichtbar ein!**
3. **Klassische Skelettbauweise (*Frame-First* — Vergleich Spätantike/Mittelalter/19. Jh.):**
   - Schweres Doppelspant-Gerippe mit stumpf kalfaterten Planken ohne Planken-zu-Planken-Verzahnung & Schotten-Zellen → einbrechender Schubverbund $\gamma$, starkes Hogging/Sagging (*Wyoming*-Effekt), höheres Eigengewicht & deutlich höhere **Poiseuille-Fugenleckage**!
- **Interaktive 3D-Wandschnitt- & Sektions-Inspektion** macht alle drei Bauweisen direkt im Modell sichtbar.

---

## 5. Smart-Layout-, Socket- & Anti-Clipping-Solver (Rust-Wasm, `< 1 ms`)

1. **Parametrische Sockets & Ellen-Anker:** Buchten, Tröge, Fässer, Göpel, Türen, Pflanztröge & Tiere docken an relative Anker an → beim Umschalten der historischen Elle wandert der gesamte Innenausbau millimetergenau mit (**0 % Clipping, 0 % Schweben!**).
2. **Keep-Out Volumes & „Smart Push-Out“-Solver:** Laufkorridore (`≥ 1,8 m`), Straßen, Prozessionsachsen, Treppen-Antritte, Tür-Schwenkbereiche, Göpel-Drehkreise & Wasserflächen sind harte Verbotszonen; ein `OBB/Capsule`-Relaxation-Solver bereinigt Überlappungen automatisch + erzeugt einen **„0-Clipping-Build-Report“**.
3. **Auto-Surface-Snap & echtes Terrain-Carving:** Bodenkontakt auf `±1 mm` inkl. dynamischer Fundament-Schürzen an Hängen + **SDF-/Masken-Terrain-Carving** für versenkte **Abzu-Tempelteiche**, Kanäle, Brunnen & Baugruben (**echte Tiefe, 0 % Z-Fighting!**).
4. **Analytische Begehbarkeit (`O(1)`):** Alle Ziggurat-Treppen, 4-Wege-Torhäuser, Brücken, Stadtmauer-Wehrgänge, Arche-Decks (D1–D3) und Ararat-Pfade butterweich begehbar ohne Per-Frame-Raycasting.

---

## 6. 1:1 Full-Scale Archäologische Welt — Die „Sintflut-Stadt“ Schuruppak (*Tell Fara*)

Aufbau im **echten historischen `1:1`-Maßstab (`~1,0 × 0,9 km`, ~70–90 Hektar, ~15.000–25.000 Einwohner)**:
- **Blender-First + Babylon-Instancing-Hybrid (`schuruppak_world_master.blend`):** Gesamte 1-km-Stadt über Collection-Instances / Geometry Nodes in Blender entworfen → Export als **~25 kompakte `.glb`-Kits (`~15–25 MB` mit `KTX2`/`Meshopt`)** + **`world_layout_schuruppak.json` (`~300 KB`)**.
- **60-FPS-Performance für 2.000–2.500 Häuser:** Thin Instances + **Snapshot Rendering** (**~15–25 Draw-Calls** für die ganze Stadt!) + **Viertel-HLODs** ab `~400 m` + **Hi-Z-/Portal-Culling** + automatisches **Wasm-Mikro-Dressing** (Krüge, Körbe, Sonnensegel, Leitern, Weinranken).
- **Archäologische Hero-Zonen (nach Koldewey, Schmidt & Tutub/Eridu ~2900–2600 v. Chr.):**
  * **Silo-Viertel:** 25–30 monumentale runde Lehmziegel-Getreidesilos (`Ø 5–8 m`) als reale Quelle für Noahs **224 Getreidezellen (Tag -30)**.
  * **Tafelhaus (*Edubba*):** Schreiberschule & Verwaltungsarchiv (*Fara-Texte*).
  * **Euphrat-Hafen:** Anleger, Speicher & dutzende *Magur*-Lastkähne.
  * **Frühdynastisches Stadtbild:** Enge organische Schattengassen (`1,5–3 m`), plankonvexe („Brotlaib“-)Ziegel, weiße Nischenfassaden, bunte **Tonstift-Mosaike**, *Mudhif*-Schilfhütten, **Abzu-Becken** & unser monumentaler **Hero-Tempelbezirk** (Hero-Ziggurat + optional frühdynastisches Tempeloval).

---

## 7. Historische, Klimatische & Wissenschaftliche Tiefen-Simulation (9 Spezial-Module)

1. **🌌 Echter Sternenhimmel um 2900 v. Chr. (Präzession der Erdachse):** Rückgerechneter Hipparcos-Katalog mit **Thuban ($\alpha$ Draconis)** als antikem Polarstern, sichtbarem **Kreuz des Südens**, umschaltbaren **sumerischen Sternbildern** (*Himmelsstier*, *Pflug*, *Hirt*) & exakten **Mondphasen** synchron zur 371-Tage-Chronologie (inkl. **Plejaden-/Kimah-Stand** laut Talmud-Tradition).
2. **🪵 Anisotrope Holzquellung („Selbstdichtung“) & Hit-Bitumen-Rheologie:** Beim Aufschwimmen (Tag 1) quellen Planken (`u: 12 % → 28 %`) selbsttätig fugendicht → Poiseuille-Bilge-Leckrate fällt über 72 h, während Holzschnecken lenzen; Arrhenius-Viskosität von **Hit-Bitumen** + Schilfasche, Kalkmehl & Fischöl (nach Umma-Texten).
3. **🧱 Keilschrift-Werftbuchhaltung (Basis-60-Tontafeln nach Fara- & Umma-Texten):** Umschaltbares „Tontafel-Logbuch“ im **Sexagesimalsystem** mit sumerischen Einheiten (`Kùš`, `Gur`, `Sila`, `Gú`) neben SI-Werten (inkl. 100-Jahre-Bauökonomie!).
4. **🤢 4. Analyse-Modus `COMFORT / MSI` (ISO-2631-Seekrankheit & Körperschall) + Torpor-Schalter:** 3D-Farbkarte durch alle 14 Sektionen (beweist Platzierung von Großtieren/Kabinen mittschiffs `S6–S8` & Fässern an Bug/Heck!) + Kleiber-Torpor-Bilanz für 371 Tage.
5. **🌱 Vitamin-C-Keimsprossen-Wannen unter dem Zôhar & Gips-Ammoniak-Chemie:** Terrakotta-Keimwannen (Gerste, Linsen, Kichererbsen) im Zôhar-Licht auf Deck 3 gegen Skorbut + $\text{NH}_3$-Bindung durch Torfmoos-Gipsmehl ($\text{CaSO}_4$).
6. **⏳ Kontinuierliche 371-Tage-Alterung & Verbrauchs-Chronologie:** Frisches Holz & Pechöfen (Tag -30) → glänzend-nasses Kopher, Algen-Wasserlinie, eingelaufene Göpel-Kreise & reales NKL-3-Kriechen (Tag 1–150) → geleerte Fässer/Silos, **abgenommene Dachplanken (Gen 8,13!)** & sprießender **Oliven-Pionierwuchs** am Ararat (Tag 151–371).
7. **🏔️ 3.000-m-Höhenphysiologie am Ararat & Wind-/Drift-Trajektorie:** Barometrische Höhenhypoxie (`~70 % p₀`, Atemfrequenz, Kälte-Energiebedarf bei Schneelast) + stilisierte **Tontafel-Driftkarte** von Schuruppak zum Ararat.
8. **🌍 Globale Breitengrad-, Höhen-, Kalender- & Synoptik-Wetterengine (durchgängiges Erdsystem!):**
   - **Kalender-Traditionsschalter nach Gen 7,11 / Talmud *Rosch ha-Schana 11b–12a*:**
     1. **Herbst-Start (`17. Cheshvan` ~Nov, Rabbi Elieser / Raschi / Seder Olam):** Start in die Nahost-Herbst-/Winterregenzeit → 150-Tage-Fahrt im Winter, Hochgebirgswinter & echte **EC1-Schneelast** auf dem `3.000-m`-Ararat!
     2. **Frühlings-Start (`17. Ijjar` ~Mai, Rabbi Joschua / Jubiläen-Qumran):** Start zur großen Euphrat-Schneeschmelzflut → Hochsommer-Hitze auf See (extremer **Rinder-THI- & Bâdgir-Härtetest!**) → frühlingshafter Auszug im Folge-Mai (Olivenzweig!).
   - **Kontinuierliche Geokoordinaten-Fahrt:** Interpolation von **Schuruppak ($\varphi \approx 31{,}8^\circ\,\text{N}$, $z \approx 12\,\text{m ü. NN}$)** bis **Ararat ($\varphi \approx 39{,}7^\circ\,\text{N}$, $z \approx 3.000\,\text{m ü. NN}$)**.
   - **Astronomische Solar-Geometrie:** Exakte Sonnendeklination $\delta(\text{Tag})$, Tageslänge, Auf-/Untergang & Zenitwinkel aus $(\varphi(t), \text{Tag})$ → steuert Kasten-Young-Strahlung, Zôhar-Lichteinfall & Keimsprossen.
   - **Adiabatische Lapse Rate (`−6,5` bis `−9,8 °C / 1.000 m`), Psychrometrie & LCL-Wolkenbasis:** Reale Höhenabkühlung; **Lifting Condensation Level (LCL)** legt die reale Wolkenuntergrenze fest → am `3.000-m`-Ararat taucht der Gipfel in tiefhängende Wolkenbänke & Nebel ein!
   - **Orographischer Steigungsregen, `0°`-Schneefallgrenze & Schmelzwasser:** Steigungsregen an Vulkanhängen, Übergang zu Schnee unter `+1,5 °C` (speist EC1-Dachschneelast + Schneegrenze), und Schmelzwasser speist direkt die **2D-SWE-Hangsturzfluten**!
   - **Synoptik, Coriolis ($f = 2\Omega \sin\varphi$) & Kaimal-Böen:** Barometrische Druckfelder (`965–1025 hPa`, triggern Tier-Unruhe vor Sturm), **+21 %** stärkerer Coriolis-Effekt im Norden (Ekman-Drift), organische Böenwalzen nach Kaimal-Spektrum.
   - **Höhen-Strahlung, Albedo-Feedback & Atmosphären-Optik:** `~30 %` dünnere Atmosphäre auf `3.000 m` (+UV tagsüber, **extremer nächtlicher Strahlungsfrost `−10 bis −15 °C`** für Bitumen & Tiere); echte Albedo (Sand `0.38`, Pech `0.05`, Schnee `0.82`); dunstiger *Schamal*-Tieflandhimmel vs. tiefblauer Ararat-Himmel + physikalisch exakter `42°/51°`-Regenbogen (Tag 371).
9. **🪓 100-jährige Bau-, Forst- & Werft-Chronologie (`Jahr −100` bis `Tag −30`):**
   - **„12-Archetypen → ~12.000 echte 3D-Einzelbalken“-Baukasten:** In Blender werden lediglich **~10–14 meisterhafte Zimmermanns-Grundmodule** gebaut (angefaste Kanten, Stirnholz, echte Zapfen/Schwalbenschwanz-Blätter: Kielbalken, Königsstütze mit Sattelholz/Kopfbandknaggen, Eichen-Wurzelknie, Schottenbohle, Blockzarge, Außenplanke mit Feder-Nut, Sparren, Dübel). **Rust-Wasm** setzt daraus vollautomatisch alle **`~12.000` Einzelbalken & Planken** als **Babylon `Thin Instances`** zusammen (**`~400k Tris`, `~6–12 Draw-Calls`, `60 FPS`!**) — jeder Balken ist einzeln anklickbar, mit `ELLE_M` skalierbar und trägt sein eigenes **`buildPhase`-Baujahr (`−100` bis `0`)**!
   - **Kluge LOD-Grenzen:** Die **`80.000` Hartholzdübel** erscheinen als echte 3D-Köpfe nur im **`LOD0 < 18 m`**-Nahbereich und an offenen Baustellen-Kanten (darüber Normalmap); ab **`> 60–80 m`** schalten Außenwände auf ein leichtes `LOD1/2`-Rumpf-Mesh.
   - **Die 6 Bauphasen in korrekter Schottenbau-Logik:**
     1. *`Jahr −100` bis `−85` (Infrastruktur):* Ausheben der `140-m`-Hellinggrube mit Basalt-Unterbau (Winkler-Baugrund), Bau von **Aquädukt**, **Göpel-Sägewerk**, **Tubal-Kain-Schmiede**, **Pechöfen** & Seilerei.
     2. *`Jahr −85` bis `−55` (Forst, Einschlag & Trocknung):* Sichtbare **Holzeinschlag-Schneisen** im Zedern-/Eichen-/Zypressen-Wald (während in älteren Schlägen junge Bäume über Jahrzehnte sichtbar nachwachsen!); Holztransport per **Zugochsen-Gespannen & Euphrat-Flößen**; jahrelange Lufttrocknung in großen Werft-Holzstapeln (`u: 65 % → 15 %` mit realem Schwindmaß!).
     3. *`Jahr −60` bis `−45` (Kiellegung & Sohle):* Verlegen der **3 Außenkiele (`6 Hände`)**, **Sohle (`5 Hände`)** & **15 Kielschweine**.
     4. *`Jahr −45` bis `−20` (Schottenbau-Gerippe!):* Aufrichten der **45 Königsstützen**, der **13 Querschotten mit 201 Blockzargen-Türen**, der **2 Längsschotten**, der **224 Janssen-Silozellen** und der **Decks D1–D3** (mit mitwachsenden Baugerüsten & 4 Werftkranen).
     5. *`Jahr −25` bis `−2` (Beplankung, Dübel, Maschinen, Dach & Kopher-Pechung):* Schließen & Aussteifen des Kastens mit **720 Eichen-Wurzelknien**, **Außenplanken & 80.000 Hartholzdübeln**; Einbau von **2×3-Ochsen-Göpeln, 6:1-Stockgetrieben, Becherwerken & Holzschnecken**; Aufsetzen von **Dach, Zôhar & 8 Bâdgiren**; Kalfaterung & **3-fache Hit-Bitumen-Pechung** (Rumpf wandelt sich von frischem Holz zu tiefem Kopher-Schwarz!).
     6. *`Jahr −2` bis `Tag −30` (Abrüsten & Bebunkerung):* Gerüst-Abbau (nur Laderampe an S7 bleibt), Anrollen der **7.920 Fässer** & Kornkarawanen aus Schuruppaks Silos.
   - **Gekoppelte Bau-Ökonomie-Bilanz:** Live-Zähler für gefällte Stämme je Holzart, nachwachsende Forstfläche, geschlagene Dübel, Tonnen Bitumen, Zimmerleute-Mannjahre & Gersten-/Bierrationen auf den sumerischen Keilschrift-Tafeln!

---

## 8. Living-World-Ökosystem (Crowds, Wildtiere, Logistik & Akustik)

1. **🚶‍♂️ Tageszeit-Crowdsystem (Rust-Wasm Flow-Fields + Mocap-VAT):** Echte mesopotamische Tagesabläufe synchron zum Sonnenstand (Morgengrauen-Wasserträger & *Tannur*-Öfen → Markt & Werft → `42 °C`-Mittagsruhe im Schatten → Abendlicht mit **Clustered Lighting**-Öllampen & Feuerschalen); `300–600` aktive Bürger im `150 m`-Umkreis mit natürlichen Mocap-Zyklen via **Babylon VAT** (`0,0 ms` CPU-Skinning, 0 Moonwalking!).
2. **🦅 4-Schichten-Wildtier- & Ökosystem (aus unseren ~35 Tierfamilien via `Mesh2Motion` + VAT):** Himmel-GPU-Boids (Störche, Reiher, Falken, abends Fledermäuse + **Rabe & Taube** an Tag 310–371), Wasser/Marschen (Fische, Libellen, Schildkröten), Herden/Steppe (Schafe, Ziegen, Esel-/Kamel-Karawanen, Gazellen) & dramatischer **Tiereinzug (Tag -7)** über die Werftrampe ins `9×8-Ellen`-Seitentor.
3. **⛵ Lebendige Fluss-, Werft- & Bord-Logistikkette:** *Magur*-Lastkähne, Wasserräder, Aquädukt, Ochsen-Holzzüge, Göpel-Sägewerk, schwenkende Krane; im Rumpf **5,5-h/d-Schichtbetrieb** der 24 Zugochsen an den 2×3-Ochsen-Göpeln (S4/S11) + Noahs Familie auf Kontrollgang.
4. **🔊 Ortsaufgelöste Akustik-Ökologie (Web Audio API, 0 Byte MP3s):** Markt/Gassen, Abzu-Tempelbezirk, Werft-Sägewerk, Meer & Rumpfinneres (Planken-Ächzen gekoppelt an $|M_y|$, 6:1-Stockgetriebe-Klacken, Tierdecks).

---

## 9. GPU-Partikelsystem & 3-Schichten-Fluid-Engine (`~2,5–3,0 ms` GPU-Budget, 60-FPS-fest!)

Direkt eingebunden über Babylon.js 9.x `ComputeShader`, `Particle Flow Maps` & `Fluid Rendering`:

1. **🎆 GPU-Compute-Partikelsystem (`50k–250k` Partikel Desktop / `20k–50k` iPad, `~0,4 ms`):**
   - Ping-Pong-Storage-Buffer + `Indirect Draw`, 0 % CPU-Last, gekoppelt an Wind, Schwerkraft, Curl-Noise, Terrain-/Deck-Kollision & **FSR-Reactive-Mask**.
   - **Effekte:** Wellen-Gischt & Slamming-Fontänen, Starkregen mit Pfützen-Spritzern, Felskanten-Wasserfall-Gischt bei Ararat-Regenströmen, Schnee am Ararat, Funken, *Tannur*-/Pechofen-/Altar-Rauch, Sägespäne, Staub, Schrotmühlen-Korn, Zôhar-Lichtstaub, Glühwürmchen; synchron flatternde Markt-Sonnensegel & Wäscheleinen.
2. **🌊 Schicht A — Makro (12-km-Ozean): WebGPU-FFT + Stokes-3-Hybrid (`~0,6 ms`):**
   - Endloser Ozean + mitlaufender **2D-Bugwellen-Ringpuffer** um den 140-m-Rumpf.
3. **💧 Schicht B — Meso (Euphrat, Abzu-Teiche, Bilge, Tag-1-Flut & Regen-/Schmelzwasser-Sturzfluten!): Gehärtete 2D-Shallow-Water-Engine (`~0,5–1,1 ms`):**
   - **Lokales `1,0-m`-Stadt-/Hang-SWE-Grid (`512²–1024²` Desktop / `256²–512²` iPad):** Fokussiert auf die aktive `1-km`-Stadt **Schuruppak + Werft** (bzw. den aktiven **Ararat-Hangsektor**), sodass selbst `2-m`-Stadtgassen, Torbögen, Abzu-Ränder & die Helling-Baugrube sauber aufgelöst werden.
   - **Automatische Wasm-Hindernis-Heightmap (`B_obstacle`):** Rust-Wasm backt beim Szenenstart 1× alle Häuser, Stadtmauern, Ziggurat & Felsen als unpassierbare Hindernisse (bei Brücken nur die **Brückenpfeiler**, nicht das Brückendeck!) → Regen- und Flutströme prallen an Mauern ab, umfließen Häuserblocks, strömen durch Stadttore und rauschen unter Brücken hindurch!
   - **Hydrologischer Pipe-Flow / Flux-Limiter + Manning-Reibung + Regen-/Schmelz-Quellterm:** Positiv-erhaltendes Schema ohne NaN-Explosionen oder Flimmern selbst bei extrem dünnen (`1–5 cm`) Sturzfluten an steilen `40°`-Ararat-Hängen; nahtloser Übergang zwischen **`SSR2`-Nässe-/Pfützenmaske (`h < 3 cm`)** und **echtem schäumendem Fließwasser (`h ≥ 3 cm`)**.
   - **Weitere Einsätze:** Physikalische Wellenringe im Abzu-Teich, Kelvin-Bugwellen der *Magur*-Boote, **schwappendes Bilge-Wasser im Rumpf** sowie das **reale Über-die-Ufer-Treten des Euphrat an Tag 1**, bis die Arche aufschwimmt!
4. **🫗 Schicht C — Mikro (Nahbereich `< 25 m` Desktop): Lokales 3D-PBF/SPH (`4k–10k` Partikel, `~1,0 ms`):**
   - 1–2 aktive Kamera-Herostellen mit **Babylon Fluid Rendering** (Archimedische Holzschnecken, Abzu-Wasserspeier, Aquädukt-Auslauf & heißes Kopher-Pech; iPad-Fallback `0,1 ms`).
5. **⛔ Bewusste Anti-Crash-Grenze:**
   - Kein globales 3D-SPH/FLIP über ganze Flüsse/Ozeane und kein 3D-Navier-Stokes-CFD für die gesamte Innenluft.

---

## 10. Unverrückbare Grundgesetze (Heiliger Kanon auch in ARCHE 3.0)

1. **First-Principles-Physik:** 0 Placebo- & Schummel-Beiwerte; alle `101+` Physik-, EC5-, Bauweisen- & Ellen-Tests sowie der automatische **0-Clipping-Report** als verbindliche CI-Gate.
2. **Bronzezeit-Authentizität:** 0 Anachronismen (Eiche D35, Zypresse C27, Zeder C18, Hainbuche, Zinnbronze, Basalt, Kopher-Pech, Hanfseile, Lehmziegel, Kalkstein, Lapislazuli).
3. **Farbschutz & 4-Modi-Reinheit:** Kopher-Pech/Außenholz unverfälscht; AgX/SSS/Detail-Normals/POM/Reflexionen/SSAO/SSCS strikt nur in `TEXTURED`; `EC5`, `THERMAL` und `COMFORT/MSI` zwingend mit `NoToneMapping`, ohne Reflexionen/Schatten-Verdunklung & mit `100 % Nativ`.
4. **Performance-Ziel:** Stabile `~60 FPS` auf Desktop (GTX 1070), iPad & Mobile durch **Babylon.js 9.x (WebGPU + native WGSL + Snapshot Rendering + Clustered Lighting)** + **TSR-Lite/FSR-Reactive-Mask/RCAS** + **Planar/`SSR2`/`SSAO2`/4-Band-CSM+`SSCS`** + **Babylon VAT (Mocap)** + **Rust-Wasm** + **4-LOD-Staffelung** + **gehärtetes 3-Schichten-Fluid-Budget (`~2,5–3,0 ms`)**.