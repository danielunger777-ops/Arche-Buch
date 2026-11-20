# ARCHE BLENDER ASSET- & MATERIAL-PIPELINE (`BLENDER_PIPELINE.md`)
> **Verbindlicher Gesamtstandard für ALLE 3D-Geometrien (Arche, Einbauten, Werft, Ur-Schinar, Ararat, Botanik, Fauna & Menschen)**  
> Kompatibel mit **ARCHE 2.0** (Three.js r128 + `Arche.Assets`) und **ARCHE 3.0** (Zero-Engine WebGPU/WebGL2 + KTX2)

---

## 1. UNVERRÜCKBARE BASIS-REGELN (KOORDINATEN, MASSSTAB & KANON)
- **Einheiten in Blender:** `Metric`, Unit Scale `1.0` (`1 Blender-Meter = 1.0 m`).
- **Biblischer Ellen-Kanon:**
  - `1 Elle` = `14.0 / 30.0 m` (`0.466667 m`)
  - `1 Handbreite` = `1/6 Elle` (`0.077778 m`)
  - `1 Fingerbreite` = `1/24 Elle` (`0.019444 m`)
  - **Arche-Außenmaß:** `300 Ellen (140,0 m)` Länge X × `50 Ellen (23,333 m)` Breite Y × `30 Ellen (14,0 m)` Höhe Z.
- **Achsen in Blender (Z-Up) vor Export:**
  - `+Z` = Oben (Himmel) | `+Y` = Vorne (Blick-/Laufrichtung bei Figuren/Tieren; Steuerbord bei Rumpf-Modulen gemäß Achskonvention) | `+X` = Längsachse Bug/Heck bzw. Rechts.
  - *Hinweis zur Rumpf-Ausrichtung:* Schiffszentrum liegt bei `X = 0` (`[-70 m .. +70 m]`), `Y = 0` (`[-11.667 m .. +11.667 m]`), Sohlen-Unterkante bei `Z = 0` (`[0 m .. +14 m]`, Außenkiele reichen bis `Z = -0.467 m`).
- **Origin & Transforms:**
  - **Jedes Asset** hat seinen Origin (`0,0,0`) mittig auf der Aufstandsfläche (`Z = 0.0`) – bei beweglichen Maschinenteilen (Göpel-Kammrad, Kurbelwelle, Kranwinde, Sturmklappen) exakt auf der **Drehachse**!
  - Vor jedem Export zwingend **`Ctrl + A → All Transforms`** (`Scale = 1,1,1`, `Rotation = 0,0,0`).
- **Standard-Export-Drehung:** Immer als **`.glb` (Binary glTF 2.0)** mit **`+Y Up` aktiviert** exportieren. Der Loader in ARCHE wendet exakt `rotation.x = +Math.PI / 2` an → dadurch bildet Blender `(X, Y, Z)` mathematisch `1:1` auf ARCHE `(X, Y, Z)` ab.

---

## 2. DIE 5 ASSET-KATEGORIEN & IHRE KONSTRUKTIONSREGELN

### Kategorie A: Die Arche & ihre 15 Einbauten-Systeme (Physik- & Schnitt-kompatibel!)
Damit **Etagen-Schnitte (`uMaxSliceZ`)**, **Bordwand-Ausblendung**, **EC5-Spannungsfarben**, **Infrarot-Thermografie** und **Maschinen-Animation** weiterhin exakt funktionieren, darf die Arche **niemals** als ein einziges statisches Mesh exportiert werden, sondern als **sauberes Modul-Set**:
1. **Struktur-Module (separate `.glb`-Dateien pro Sichtbarkeits-Layer):**
   - `ark_sole_and_keels.glb` (Sohle 5 Hände + 3 Außenkiele 6 Hände + 45 Königsstützen)
   - `ark_outer_wall_bb.glb` & `ark_outer_wall_sb.glb` (Bordwände 4 Hände, inkl. 9×8-Ellen-Torrahmen S7 & beweglichem Torflügel `ark_side_gate.glb`)
   - `ark_long_bulkheads.glb` & `ark_trans_bulkheads.glb` (2 Längs- & 13 Querschotten 3 Hände mit exakten 201 Türdurchbrüchen & geschlossenen Siloblöcken S3/6/9/12)
   - `ark_decks_d1_d3.glb` (Decks D1–D3 mit Durchbrüchen & Rampen-Öffnungen)
   - `ark_roof_and_zohar.glb` (Dach + Zôhar-Firstschlitz + abnehmbare Dachsektion)
   - `ark_badgir_unit.glb` & `ark_shutter_flap.glb` (instanziiert für 8 Zweikammer-Bâdgire & bewegliche Sturmklappen!)
   - `ark_oak_knee_unit.glb` & `ark_peg_cluster.glb` (720 Wurzelknie & Holzdübel-Detail)
2. **Einbauten & Maschinenbau-Module (animierte Teile mit Dreh-Origin!):**
   - `prop_goepel_rotor.glb`, `prop_lantern_pinion.glb`, `prop_archimedean_screw.glb`, `prop_paternoster_frame.glb`, `prop_paternoster_bucket.glb`
   - `prop_barrel_oak.glb` (R=4 Hände, L=2 Ellen → 1 Instanz-Mesh für alle 7.520+ Fässer!), `prop_amphora_svalbard.glb`, `prop_zeer_cooler.glb`, `prop_galley_basalt.glb`, `prop_carpenter_workbench.glb`, `prop_hay_bale.glb`, `prop_grain_silo_bay.glb`
3. **Pflicht-Tagging für Struktur-Module (`Color Attribute` / `UV_1`):**
   - Jeder Vertex in Struktur-Meshes nutzt Welt-/Schiffslokal-Koordinaten `(x, y, z)` für EC5/Thermografie **plus** ein optionales `Color Attribute` (`Col_Meta`: `R = materialType [Eiche/Zypresse/Zeder/Basalt]`, `G = elementGroup [Kiel/Wand/Schott/Deck/Dach/Einbau]`, `B = fixTag`). Dadurch funktioniert jede EC5- und Thermo-Einfärbung exakt wie bei der prozeduralen Geometrie!

---

### Kategorie B: Botanik & Wälder (10 Baumarten des Vorderen Orients, Sträucher & Pflanzen)
1. **Standard-Artenkatalog (10 Baumarten × 15 Varianten × 4 Altersstadien):**
   - **Libanon-Zeder (`cedar`), Mittelmeer-Zypresse (`cypress`), Orientalische Eiche (`oak`), Orientalische Hainbuche (`hornbeam`), Dattelpalme (`palm`), Schirmakazie (`acacia`), Olivenbaum (`olive`), Sykomore/Feige (`fig`), Euphrat-Pappel (`poplar`), Atlas-Terebinthe (`terebinth`)** sowie weitere Pflanzen (`shrub_*`, `grass_tuft_*`, `reed_*`, `vine_*`).
   - Master-Texturen: **10-Streifen Bark Trim (`2048×1024`)** + **5×4 Leaf Atlas (`2048×2048`, 20 Zellen)**.
2. **Pflicht-Aufbau pro Pflanzen-`.glb`:**
   - **Material-Slot 0 (`Bark`):** Echter 3D-Stamm & mehrstufige Äste (abnehmende Ast-Radien, Wurzelanläufe am Boden).
   - **Material-Slot 1 (`Foliage`):** Gewölbte mehrsegmentige Blatt-Karten (*Curved Foliage Sprays* mit scharfem `alphaTest = 0.35..0.44` + `alphaToCoverage`, niemals flache grüne Kugeln!).
   - **Vertex Color (`Col_Wind`):**
     - `R` = Wind-Biegegewicht (`0.0` am Wurzelstock → `1.0` in den Astspitzen, für die durchlaufende Wind-Böenwelle!)
     - `G` = Blatt-Flatterphase (leichtes Rauschen pro Ast/Blattbüschel)
     - `B` = Baked Ambient Occlusion (Kronen-Inneres dunkler als Spitzen!)
3. **Verbindlicher 4-LOD-Standard & weiche Übergänge für JEDE Pflanze & Architektur/Werft (Pflicht in allen `build_*.py`!):**
   Jede Pflanzen-Variante (`<species>_<stage>_<var>_LOD0..LOD3`) sowie modulare Architektur-/Werft-Baugruppen müssen exakt **4 Detailstufen** mit den einheitlichen Distanzbändern **`150 m / 500 m / 1.500 m / 3.000 m`** exportieren (Ararat bis `3.000 m` mit reduzierter Baumdichte):
   - **`LOD0` (Hero-Nahbereich `0–150 m`):** `5.000–14.000 Tris` (`≥ 5×` Detail gegenüber Erstgeneration: tertiäre Zweige, gewölbte 2×2-Segment-Laubkarten, 10–12 Stamm-Facetten).
   - **`LOD1` (Mittel-Nah `150–500 m`):** `1.800–4.200 Tris` (Sekundäräste, gestaffelte gekreuzte Blattkarten, 6–7 Stamm-Facetten).
   - **`LOD2` (Mittel-Fern `500–1.500 m`):** `350–850 Tris` (Hauptkrone + vereinfachtes Astgerüst).
   - **`LOD3` (Horizont `1.500–3.000 m`):** `40–140 Tris` (kompakter 3-Kant-Stamm + gekreuzte Ganzkronen-Proxy-Karten; Ararat mit reduzierter Baumdichte).
   - **Pflicht-Crossfade & Dither-Verbot (Kein Aufploppen, kein Punkte-Sieb!):** Laubkronen (`Foliage`) überblenden über überlappende Distanzbänder (`±13–18 %` der Schwellendistanz, zzgl. `120–240 m` Horizont-Ausblendung) mittels komplementärem **Screen-Space-Dithering** (`lodInterleavedNoise(gl_FragCoord.xy)`): gerade LODs (`LOD0/LOD2`) behalten `_dither < visibility`, ungerade (`LOD1/LOD3`) behalten `_dither >= (1.0 - visibility)`. **Ausdrückliches Verbot:** Auf **Baumstämmen (`Bark`)** und **Gebäudewänden** darf **niemals** Screen-Space-Dithering angewendet werden (verhindert sichtbares Punkte-Sieb auf soliden Flächen).

---

### Kategorie C: Architektur, Werft, Ur-Schinar & Ararat (Modulare Kits!)
Niemals ganze Dörfer/Städte als ein Riesen-Mesh exportieren! Stattdessen **wiederverwendbare Modul-Kits** für Instancing:
1. **Werft & Kapitel 13:**
   - `env_crane_aframe.glb`, `env_crane_winch.glb`, `env_scaffold_bay.glb`, `env_ramp_60c.glb`
   - `env_sawmill_capstan.glb`, `env_sawmill_frame.glb`, `env_sawpit_shed.glb`
   - `env_pitch_kiln.glb`, `env_smithy_forge.glb`, `env_charcoal_kiln.glb`, `env_aqueduct_arch.glb`, `env_tent_nomad.glb`
2. **Ur-Schinar, Kanalauen & Dörfer:**
   - `city_mudbrick_house_01..04.glb`, `city_courtyard_insula_01..02.glb`, `city_gate_ur.glb`, `city_wall_segment.glb`, `city_ziggurat_temple.glb`, `city_mudhif_reed_hut.glb`, `city_grain_silo.glb`, `city_kiln.glb`
   - `env_canal_bridge.glb`, `env_sluice_gate.glb`, `env_shaduf.glb`, `env_waterwheel.glb`, `boat_magur_01..02.glb`
3. **Ararat:**
   - `ararat_altar_cyclopean.glb` (geschichteter unbehauener Naturstein + Opferplatte + Scheite), `ararat_gangway_module.glb`, `ararat_camp_props.glb`, `ararat_basalt_boulder_01..03.glb`.
4. **Terrain-Synchronisation (Pflicht!):**
   - Große Geländebauten, Häuser und Stege haben `0.3–0.6 m` tief in den Boden reichende **Fundament-Sockel (`Z = -0.5 .. 0.0`)**, damit an leichten Hanglagen niemals eine Ecke in der Luft schwebt!
   - Optional exportierbare Geländemeshes müssen exakt der analytischen Höhenfunktion (`evalShipyardTerrainZ` / `evalAraratTerrainZ`) folgen oder ihre Höhen-Map (`terrain_height.png` / `.raw`) synchron für die Physik mitliefern.

---

### Kategorie D: 2.800+ Tierarten (30 Familien + Shape Keys + GPU-DNA)
Um über 2.800 Gattungen ohne Draw-Call-Explosion darzustellen, werden **niemals** 2.800 `.glb`-Dateien erstellt:
1. **~30 anatomische Familien-Meshes (`assets/blend/families/*.glb`):** z. B. `fam_bovid`, `fam_cervid`, `fam_felid`, `fam_canid`, `fam_equid`, `fam_camelid`, `fam_ursid`, `fam_proboscid`, `fam_rhino_hippo`, `fam_giraffid`, `fam_suid`, `fam_primate`, `fam_rodent`, `fam_bat`, `fam_sauropod`, `fam_theropod`, `fam_croc`, `fam_turtle`, `fam_raptor`, `fam_ratite`, `fam_waterfowl`, `fam_passerine` (`1.200–3.000 Tris`, `1 Material`).
2. **4–6 Blender Shape Keys pro Familie (exportiert als glTF Morph Targets):**
   `Key_NeckLegLength`, `Key_BodyBulk`, `Key_SnoutHead`, `Key_ManeHumpCrest`, `Key_HornsAntlersTusks`.
3. **Einheitliches Vertex-Part-Tagging (`Color Attribute` `Col_Rig`):**
   Markiert exakt Beine (`VL/VR/HL/HR`), Hals/Kopf, Flügel und Schwanz sowie lokale Gelenk-Drehpunkte für die GPU-Lauf-, Atem-, Gras- und Flug-Animation (inkl. `aMorphType` / GPU-Einzug).
4. **Arten-DNA (`assets/data/species_dna.json`):**
   Ordnet alle 2.800 Gattungen per `(familyId, shapeWeights[5], scaleXYZ, patternType, colorPrimary, colorSecondary, gaitFreq)` zu.

---

### Kategorie E: Hero-Charaktere & Arbeiter (Noah, Familie & Knechte)
- `char_noah_hero.glb`, `char_wife_hero.glb`, `char_son_01..03.glb`, `char_daughter_01..03.glb` (4.000–8.000 Tris), sowie instanziierbare Arbeiter-Varianten (`char_worker_01..03.glb`, 1.200–2.500 Tris) für Werft & Ur-Schinar.
- Einheitliche Skelett-/Part-Tags für Gehzyklus, Ruder-/Säge-/Gebets-Posen und wehende Leinen-Gewänder.

---

## 3. VOLLE BLENDER-MATERIALIEN, PBR-BAKING, SSS & REALISMUS-TRICKS

### 3.1 Automatisches PBR-Baking (`export_arche_glb.py`)
Komplexe Blender-Shader-Nodes (Noise, Musgrave, Holzmaserung, Verwitterung) werden beim Export automatisch auf saubere UV-Maps gebacken:
- **`BaseColor` (`Albedo`)** inkl. gebackener **Pointiness-Kantenabnutzung** (heller an exponierten Kanten) & **Cavity-Schmutz/Ruß** (dunkler in Fugen/Ritzen).
- **`Normal`** (Tangent-Space, sauber geglättet / Bevel-Kanten).
- **`ORM`-Packed Texture** (spart 2 von 3 Textur-Slots auf Mobile/iPad!):
  - **R** = Ambient Occlusion (`AO` → steuert auch *Lagarde Specular Occlusion* gegen Wachsglanz in Falten!)
  - **G** = `Roughness` (inkl. polierter Kanten & matter Fugen)
  - **B** = `Metallic` (`0.0` Holz/Stein/Haut/Stoff, `1.0` Zinnbronze/Schmiedeeisen)

### 3.2 Native glTF-2.0-Physical-Erweiterungen
- **Samt, Wolle, Leinen & Tierfell:** `Principled BSDF → Sheen Weight / Tint` (`KHR_materials_sheen`).
- **Feuchte Nasen, Augen, frisches Kopher-Pech & lackierte Bronze:** `Coat Weight / Roughness` (`KHR_materials_clearcoat`).
- **Geschliffenes Holz, gehämmerte Bronze, Haar & glattes Fell:** `Anisotropic / Rotation` (`KHR_materials_anisotropy`).
- **Schillerndes Tauben-/Rabengefieder & Kopher-Ölfilm:** `Iridescence` (`KHR_materials_iridescence`).

### 3.3 Echtzeit-Subsurface-Scattering (SSS via Thickness-Bake + GPU-Translucency)
Da Browser kein Cycles-Raytracing-SSS ausführen können:
- Blender backt für Haut (Noah & Familie), Tierohren, Vogelflügel, Blätter und Zeltleinen eine **`Thickness`-Maske** (dünne Bereiche = hell, dicke Bereiche = dunkel) + hinterlegt im Material `sssColor` (z. B. warmes Blutrot/Bernstein `vec3(0.88, 0.24, 0.10)` bei Haut/Ohren, Blattgrün bei Laub).
- Der Engine-Shader berechnet daraus **Warm-Wrap-Diffuse + Sonnen-Gegenlicht-Translucency** in `< 0,1 ms` (GTX 1070 & iPad-kompatibel!).

### 3.4 Engine-Finishing-Hooks, 5 HDR-/AgX-Regeln & Nahbereich-Schärfe
- **Die 5 verbindlichen HDR-/AgX-Regeln (1:1-Abgleich Blender 4 AgX ↔ Engine):**
  1. **Physikalischer Albedo-Korridor (`0.04 .. 0.85`):** Niemals tiefschwarz (`< 0.04`) oder klinisch reinweiß (`> 0.85`) baken, damit Blender-4-AgX (`THREE.CustomToneMapping`) weder Schatten absaufen noch Spitzlichter ausbrennen lässt.
  2. **HDR-Emission (`KHR_materials_emissive_strength`):** Feuer, Glut, Öllampen und Schmiedeherde nutzen physikalische `emissiveStrength`-Werte statt überdrehter Albedo-Farben.
  3. **0 eingebackene Sonnenschatten:** Albedo-Maps enthalten **keine** gerichteten Sonnenschatten (nur subtile lokale AO/Cavity), da direkte Beleuchtung und 4-Band-Schatten-LOD dynamisch in Echtzeit erfolgen.
  4. **Farbraum-Disziplin (`sRGB` vs. `Linear/Non-Color`):** `BaseColor` und `Emissive` strikt in **`sRGB`**; `Normal`, `ORM` (`AO/Roughness/Metallic`) und `Thickness` strikt in **`Linear / Non-Color`**.
  5. **Roughness-Spreizung:** Bewusste Spreizung zwischen mattem Lehm/Stein/Stoff (`0.72–0.95`), verwittertem Holz (`0.55–0.82`) und feuchtem Pech/polierter Bronze (`0.12–0.38`) gegen flachen Plastik-Look.
- **Haar-/Fell-/Feder-Cards:** Bärte, Löwenmähnen und Flügelspitzen nutzen außen Alpha-Karten mit `alphaToCoverage` statt klobiger Geometrie.
- **Dynamische Welt-Kopplung in `Arche.Assets` / ARCHE 3.0:**
  - **Ground-Contact Dirt (`zLocal < 0.45 m`):** Automatischer subtiler Staub-/Lehmansatz an Hufen, Säumen, Gebäudesockeln und Altären.
  - **Nässe-Kopplung (`uWetness`):** Poren-Abdunklung und spiegelnde Nässe bei Regen/Flut.
  - **Nahbereich-Textur-LOD (`0–24 m` + `Anisotropy 8×`):** Hochfrequente Poren-/Web-/Holzkorn-Detail-Normalmap im Nahbereich (`0–24 m`) kombiniert mit **`Anisotropy 8×`** für gestochen scharfe Schrägansichten.
  - **Stochastisches LOD-Crossfading (`uLodFadeBand` / `Arche.Assets.configureSmoothLODGroup`):** Verbindliche weiche Dither-Überblendung für Laub (`Foliage`) zwischen allen LOD-Stufen (`150 / 500 / 1.500 / 3.000 m`) ohne Geometrie-Popping (WebGL1-kompatibel über `gl_FragCoord.xy`) — **strikt verboten auf Baumstämmen (`Bark`) und Gebäudewänden**.
- **Analyse-Reinheit (PFLICHT!):** Alle Material-, AgX-, SSS-, SSCS-, Schmutz-, Detail-Normal- und Nässe-Effekte sind **nur im `TEXTURED`-Modus** aktiv. In **EC5-Auslastung** und **Infrarot-Thermografie** (`NoToneMapping`) bleiben die Farben strikt unverfälscht!

---

## 4. POLY-, TEXTUR-, BAKE- & SPEICHER-BUDGETS (iPAD- & GTX-1070-SICHER)

| Asset-Klasse | Max. Tris (`LOD0` / `LOD1`) | Max. Draw-Calls | Textur-Größe |
| :--- | :---: | :---: | :---: |
| **Arche Struktur-Modul** | 2.000 – 15.000 (`LOD1`: 1.000–4.000) | 1–2 | 1024×1024 (kachelnd / Trim-Sheet!) |
| **Hero-Unikate & Kultstätten** *(Steinaltar, Ziggurat …)* | 6.000 – 12.000 (`LOD1`: 1.800–2.500) | 1–2 | 1024×1024 |
| **Hero-Charakter** *(Noah & Familie)* | 4.000 – 8.000 (`LOD1`: 1.500–2.500) | 1–2 | 1024×1024 |
| **Tier-Familie** *(~30 Familien + Shape Keys)* | 1.200 – 3.000 | 1 (Instanced) | 512×512 |
| **Baum- / Pflanzen-Variante** *(4 LODs, Master-Atlas)* | `LOD0`: 5.000–14.000 \| `LOD1`: 1.800–4.200 \| `LOD2`: 350–850 \| `LOD3`: 40–140 | 2 (oder 1 gepackt) | 2048×2048 Leaf / 2048×1024 Bark |
| **Gebäude / Werft-Modul** *(Ur-Schinar, Kran …)* | 300 – 2.500 | 1 | 512–1024 Trim-Sheet |
| **Kleinst-Requisiten** *(Fass, Amphore, Werkzeug)* | 150 – 800 | 1 (Instanced) | 512×512 |

### 4.1 Verbindliche Bake-Optimierung (Sweet Spot für Ryzen 7 2700X + GTX 1070)
Damit High-to-Low-Poly-Bakes in **~10–25 Sekunden** sauber durchlaufen statt Minuten zu blockieren:
- **High-Poly-Quelle (`40.000 – 70.000 Tris`):** Geometrie-Details in `bpy`-Skripten bevorzugt über Blenders schnelle C-Modifier (`Subdivision Surface` + `Displace` mit Voronoi/Noise) statt langsamer Python-Einzelvertex-Schleifen erzeugen.
- **Cycles Device:** Bevorzugt **CUDA (GTX 1070)** aktivieren (mit automatischem CPU-Fallback für Ryzen 7 2700X, falls headless kein CUDA-Kontext greift).
- **Sample-Sparregel pro Pass:**
  - `Normal`, `BaseColor`, `Roughness`, `Metallic`, `Emissive`: **nur `2–4 Samples`** (diese Maps besitzen kein Lichtrauschen!).
  - `Ambient Occlusion (AO)` & `Thickness (SSS)`: **`16–24 Samples`** mit aktiviertem **OpenImageDenoise (OIDN)**.
- **Max. Bake-Auflösung:** `1024×1024 px` für Hero-Assets / Trim-Sheets, `512×512 px` für Massen-Instanzen (Tiere/Requisiten).

### 4.2 VRAM- & Mobil-Schutz
- **Trim-Sheets (`2048×1024`) statt tausender Einzeltexturen:** Gebäude in Ur-Schinar (Lehmziegel, Schilfdach, Ocker-Markise, Zedernbalken), Werft-Module, Rinden (`Bark`) sowie Rumpf-Module teilen sich **gemeinsame `2048×1024`-Trim-Sheets** (inkl. `Anisotropy 8×`), damit iPads und Desktop-GPUs mit minimalen Draw-Calls und Texture-Binds auskommen.
- **ARCHE 3.0 Zielformat:** Texturen werden zusätzlich nach **KTX2 / Basis Universal (BC7/ASTC)** transkodiert (75–85 % VRAM-Ersparnis).

---

## 5. ORDNERSTRUKTUR & AUTONOME ANTIGRAVITY-ERSTELLUNG (`bpy`)

```text
/assets/
  /blend/
    /ark/                     ← Arche-Module & Einbauten
    /botany/                  ← 10 Baumarten, Sträucher, Gräser, Oliven
    /world/                   ← Werft-Module, Ur-Schinar-Kits, Ararat-Altar
    /worlds/                  ← Komplette Welt-Szenen (Werft/Ur-Schinar, Ararat)
    /families/                ← ~30 Tier-Familien mit Shape Keys
    /characters/              ← Noah, Familie & Arbeiter
  /glb/                       ← Exportierte .glb-Dateien (gleiche Unterordner)
  /worlds/                    ← Exportierte Welt-Daten (Heightmap, Splatmap, world_layout_*.json)
  /textures/                  ← Gemeinsame 2048×1024-Trim-Sheets, Detail-Normals, Blatt-Atlas
  /scripts/                   ← Parametrische Blender-Python-Generatoren (build_*.py)
  /previews/                  ← Automatische Kontroll-Renderings (PNG, inkl. world_*.png)
  /data/species_dna.json      ← 2.800-Arten-DNA-Tabelle
  export_arche_glb.py         ← Master-Exporter (Apply Transforms, Bake, LODs, Budget-Check)
  manifest.json               ← Slot-Registry für ARCHE 2.0 & 3.0
```

### 5.1 Verbindlicher 3-Punkte-`bpy`-Workflow für Antigravity
1. **Parametrisch bauen & verifizieren:** Jedes Asset oder Welt-Kit wird über ein reproduzierbares `assets/scripts/build_*.py` erzeugt (Metric `1.0`, Origin auf `Z = 0`, `Ctrl+A → All Transforms`, 4 LODs `150 / 500 / 1.500 / 3.000 m`, kein Dithering auf `Bark`/Wänden).
2. **Automatisches Baking, Export & Preview-Render:** `export_arche_glb.py` backt PBR-Maps (`sRGB` BaseColor/Emissive, `Linear` Normal/ORM/Thickness, 5 HDR-/AgX-Regeln), prüft Poly-/Draw-Call-Budgets, exportiert `.glb` (`+Y Up`) sowie bei Welten `Heightmap`, `Splatmap` und `world_layout_*.json` nach `assets/worlds/` und rendert ein AgX-Kontrollbild nach `assets/previews/*.png` (bzw. `world_*.png`).
3. **Manifest-Registrierung & Visual-Critic-Abnahme:** Asset in `assets/manifest.json` eintragen, `node verify_arche.js` + `node qa_arche.js` ausführen und alle `assets/previews/*.png` sowie `scratch/qa_*.png` streng nach `rules/visual-critic.md` im 1:1-AgX-Vergleich abnehmen.