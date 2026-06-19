#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Télécharge les lieux-dits cadastraux (GeoJSON gzippé) de tous les départements
métropolitains, calcule le centroïde de chaque polygone et empile le tout
dans un unique GeoPackage de points.
Source : https://cadastre.data.gouv.fr/data/etalab-cadastre/<DATE>/geojson/departements/<XX>/cadastre-<XX>-lieux_dits.json.gz
"""
import gzip
import io
import os
import sys
import time
import urllib.request
import urllib.error

import geopandas as gpd

DATE = "2025-12-01"
BASE = f"https://cadastre.data.gouv.fr/data/etalab-cadastre/{DATE}/geojson/departements"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_GPKG = os.path.join(OUT_DIR, "lieux_dits_centroides_france.gpkg")
LAYER = "lieux_dits_centroides"

# Codes départements : 01..95 sauf le 20 (Corse = 2A / 2B)
codes = [f"{i:02d}" for i in range(1, 96) if i != 20] + ["2A", "2B"]
codes.sort()


def fetch(code, retries=3):
    url = f"{BASE}/{code}/cadastre-{code}-lieux_dits.json.gz"
    last = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read()
            return gzip.decompress(raw)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None  # pas de fichier pour ce département
            last = e
        except Exception as e:  # noqa
            last = e
        time.sleep(2 * attempt)
    raise RuntimeError(f"Echec téléchargement {code}: {last}")


def main():
    if os.path.exists(OUT_GPKG):
        os.remove(OUT_GPKG)

    total_pts = 0
    done = []
    skipped = []
    first = True

    for code in codes:
        print(f"[{code}] téléchargement…", flush=True)
        data = fetch(code)
        if data is None:
            print(f"[{code}] absent (404), ignoré")
            skipped.append(code)
            continue

        gdf = gpd.read_file(io.BytesIO(data))
        if gdf.empty:
            print(f"[{code}] vide, ignoré")
            skipped.append(code)
            continue

        # GeoJSON cadastre = WGS84 (EPSG:4326)
        if gdf.crs is None:
            gdf = gdf.set_crs(4326)

        # Centroïde calculé en Lambert-93 (projeté) puis reprojeté en 4326
        cent = gdf.to_crs(2154).geometry.centroid
        gdf = gdf.set_geometry(cent).to_crs(4326)
        gdf["dep"] = code

        n = len(gdf)
        total_pts += n
        gdf.to_file(
            OUT_GPKG, layer=LAYER, driver="GPKG",
            mode="w" if first else "a",
        )
        first = False
        done.append(code)
        print(f"[{code}] {n} centroïdes ajoutés (total {total_pts})", flush=True)

    print("\n=== TERMINÉ ===")
    print(f"GeoPackage : {OUT_GPKG}")
    print(f"Couche     : {LAYER} (points, EPSG:4326)")
    print(f"Total      : {total_pts} centroïdes, {len(done)} départements")
    if skipped:
        print(f"Ignorés    : {', '.join(skipped)}")


if __name__ == "__main__":
    main()
