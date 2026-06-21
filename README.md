# Lieux-dits cadastraux → centroïdes (France métropolitaine)

Script Python qui télécharge les **lieux-dits cadastraux** (GeoJSON gzippé) de
tous les départements métropolitains depuis
[cadastre.data.gouv.fr](https://cadastre.data.gouv.fr) (données Etalab),
calcule le **centroïde** de chaque polygone, applique un **nettoyage
orthographique des noms** (underscores, espaces multiples, apostrophes et
tirets espacés — ex. `L ' ETANG` → `L'ETANG`, `SAINT - JEAN` → `SAINT-JEAN`)
et empile le tout dans un unique **GeoPackage de points**.

## Source des données

```
https://cadastre.data.gouv.fr/data/etalab-cadastre/<DATE>/geojson/departements/<XX>/cadastre-<XX>-lieux_dits.json.gz
```

Départements traités : `01` → `95` (+ `2A` / `2B` pour la Corse ; le code `20`
n'existe pas). Les départements sans fichier publié (ex. Paris `75`) sont
ignorés sans interrompre le traitement.

## Traitement

- Téléchargement et **décompression gzip en mémoire** (aucun fichier temporaire)
- Centroïdes calculés en **Lambert-93 (EPSG:2154)** puis reprojetés en
  **WGS84 (EPSG:4326)** — calcul géométriquement correct
- **Nettoyage orthographique des noms** (casse d'origine préservée), écrit dans
  une nouvelle colonne `nom_clean` (le `nom` brut est conservé) :
  - underscores → espace : `CHAUSSEE_COULAZ` → `CHAUSSEE COULAZ`
  - espaces multiples réduits : `CHAMP   MACONNAIS` → `CHAMP MACONNAIS`
  - apostrophe recollée : `L ' ARQUEBUSE` → `L'ARQUEBUSE`
  - article élidé écrit avec une espace : `L ETANG` → `L'ETANG`
  - tiret espacé recollé : `SAINT - LAZARE` → `SAINT-LAZARE`
  - apostrophe typographique → droite : `’` → `'`
- Ajout d'une colonne `dep` (code département)
- Sortie : `lieux_dits_centroides_france.gpkg`, couche `lieux_dits_centroides`
  (points), attributs `nom`, `nom_clean`, `commune`, `created`, `updated`, `dep`

## Prérequis

```bash
pip install geopandas pyogrio shapely
```

## Utilisation

```bash
python compile_lieux_dits.py
```

Le millésime des données se change via la variable `DATE` en tête de script.
