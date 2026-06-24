# Lieux-dits cadastraux → points (France métropolitaine)

Script Python qui télécharge les **lieux-dits cadastraux** (GeoJSON gzippé) de
tous les départements métropolitains depuis
[cadastre.data.gouv.fr](https://cadastre.data.gouv.fr) (données Etalab),
calcule pour chaque polygone un **point représentatif** (garanti à l'intérieur
de la géométrie), applique un **nettoyage
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
- **Point représentatif** calculé via `representative_point()`
  ([GeoPandas](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoSeries.representative_point.html)
  / Shapely / GEOS `InteriorPointArea`) : le point est **garanti à l'intérieur**
  du polygone, contrairement au centroïde qui peut tomber hors d'une géométrie
  concave ou multipartie. Sortie en **WGS84 (EPSG:4326)**
- **Nettoyage orthographique des noms** (casse d'origine préservée), écrit dans
  une nouvelle colonne `nom_clean` (le `nom` brut est conservé) :
  - underscores → espace : `CHAUSSEE_COULAZ` → `CHAUSSEE COULAZ`
  - espaces multiples réduits : `CHAMP   MACONNAIS` → `CHAMP MACONNAIS`
  - lettres isolées recollées : `C O U L A U D` → `COULAUD`,
    `A   L A   M A I S O N N E T T E` → `A LA MAISONNETTE`
  - apostrophe recollée : `L ' ARQUEBUSE` → `L'ARQUEBUSE`
  - article élidé écrit avec une espace : `L ETANG` → `L'ETANG`
  - tiret espacé recollé : `SAINT - LAZARE` → `SAINT-LAZARE`
  - apostrophe typographique → droite : `’` → `'`
  - parenthèses supprimées : `( LE BOURG-NORD )` → `LE BOURG-NORD`
  - caractères spéciaux en tête/fin supprimés : `- BLAISOT SUD` → `BLAISOT SUD`
  - noms sans aucune lettre vidés : `?`, `.`, `9999` → *(vide)*
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
