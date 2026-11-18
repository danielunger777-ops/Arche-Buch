# Visual Critic Gate

Nach jeder Änderung an 3D-Geometrien, Shadern, Botanik, Fauna, Beleuchtung, UI oder Blender-Assets ist eine **strenge, kritische Sichtprüfung** Pflicht – **niemals** nur blind auf „0 Console-Errors“ verlassen!

## 1. Zu prüfende Bilder
- **Blender-Assets:** Alle neu erzeugten `assets/previews/*.png`.
- **Live-Szene (`node qa_arche.js`):** Alle relevanten `scratch/qa_*.png` (mindestens geänderte Bereiche + `overview` + `ararat_altar` + `botany_close` + `mobile_ipad`).

## 2. Die 7 Pflicht-Kriterien (gnadenlos gegenprüfen!)
Jeder Screenshot wird ausdrücklich auf folgende Fehler untersucht:
1. **Bodenkontakt & Schweben:** Schwebt irgendein Baumstamm, Strauch, Haus, Altarstein, Steg, Kran oder Tier über `evalShipyardTerrainZ` / `evalAraratTerrainZ`?
2. **Clipping & Durchdringung:** Stecken Bäume in Häusern/Straßen, schneiden Felsen/Wasser in trockene Bereiche, schneiden Tiere durch Schotten/Decken?
3. **Material, Licht & HDR-Balance:** Wirken Flächen wie flaches Plastik? Brennt Albedo weiß aus? Fehlen Kontrast, Kontaktschatten oder Tiefenstaffelung (Luftperspektive/Nebel)?
4. **Alpha- & Shader-Artefakte:** Sehen Blätter/Gräser/Feuer/Rauch wie harte rechteckige Karten/Kugeln aus? Gibt es Z-Fighting-Flimmern oder dunkle Texturnähte?
5. **Ausrichtung & Bewegung:** Schauen/laufen Tiere und Arbeiter entlang ihres Pfads (`+Y`)? Liegen Seile/Bögen/Brücken sauber an?
6. **UI & Lesbarkeit (`1440×900` & iPad-Emulation):** Überlappt ein HUD-Element, Panel, Tooltip oder 3D-Label? Wird etwas abgeschnitten?
7. **Soll-Abgleich:** Entspricht das sichtbare Ergebnis *tatsächlich* allen Anforderungen des Auftrags (nicht nur „irgendwie vorhanden“)?

## 3. Urteil & Pflicht-Schleife (max. 2 Runden)
- Bewerte jedes Bild ehrlich mit **`PASS`**, **`MINOR`** oder **`FAIL`** (inkl. exakter Beschreibung, *wo im Bild* der Makel sitzt!).
- Bei **`FAIL`** (oder sichtbaren Geometrie-/Shader-/UI-Fehlern): **Sofort gezielt nachbessern**, `node verify_arche.js` + `node qa_arche.js` erneut laufen lassen und den neuen Screenshot nochmals prüfen – **erst bei sauberem Bild darf „fertig“ gemeldet werden!**