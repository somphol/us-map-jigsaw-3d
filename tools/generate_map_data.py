#!/usr/bin/env python3
"""Build compact projected state geometry for the US Map Jigsaw game.

Source: PublicaMundi US states GeoJSON (public domain boundaries derived from
the US Census Bureau). Coordinates are projected with an Albers conic
projection tuned for the contiguous United States, normalized into the
game's world units, and simplified with Douglas-Peucker.
"""
import json
import math
import os
import urllib.request

SOURCE = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "mapdata.js")

PLAYABLE = [
    "California", "Texas", "Florida", "New York", "Illinois", "Pennsylvania",
    "Ohio", "Michigan", "Georgia", "North Carolina", "Washington", "Arizona",
    "Colorado", "Montana", "Minnesota", "Missouri", "Tennessee", "Virginia",
    "Oregon", "Utah", "Nevada", "Louisiana", "Alabama", "Kentucky", "Maine",
    "New Mexico", "South Carolina", "Iowa", "Arkansas", "Kansas",
]

ABBR = {
    "Alabama": "AL", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL",
    "Georgia": "GA", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN",
    "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
    "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI",
    "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
    "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
    "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
    "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
}

CAPITAL_COORDS = {
    "California": ("Sacramento", 38.5816, -121.4944),
    "Texas": ("Austin", 30.2672, -97.7431),
    "Florida": ("Tallahassee", 30.4383, -84.2807),
    "New York": ("Albany", 42.6526, -73.7562),
    "Illinois": ("Springfield", 39.7817, -89.6501),
    "Pennsylvania": ("Harrisburg", 40.2732, -76.8867),
    "Ohio": ("Columbus", 39.9612, -82.9988),
    "Michigan": ("Lansing", 42.7325, -84.5555),
    "Georgia": ("Atlanta", 33.7490, -84.3880),
    "North Carolina": ("Raleigh", 35.7796, -78.6382),
    "Washington": ("Olympia", 47.0379, -122.9007),
    "Arizona": ("Phoenix", 33.4484, -112.0740),
    "Colorado": ("Denver", 39.7392, -104.9903),
    "Montana": ("Helena", 46.5891, -112.0391),
    "Minnesota": ("Saint Paul", 44.9537, -93.0900),
    "Missouri": ("Jefferson City", 38.5767, -92.1735),
    "Tennessee": ("Nashville", 36.1627, -86.7816),
    "Virginia": ("Richmond", 37.5407, -77.4360),
    "Oregon": ("Salem", 44.9429, -123.0351),
    "Utah": ("Salt Lake City", 40.7608, -111.8910),
    "Nevada": ("Carson City", 39.1638, -119.7674),
    "Louisiana": ("Baton Rouge", 30.4515, -91.1871),
    "Alabama": ("Montgomery", 32.3668, -86.3000),
    "Kentucky": ("Frankfort", 38.2009, -84.8733),
    "Maine": ("Augusta", 44.3106, -69.7795),
    "New Mexico": ("Santa Fe", 35.6870, -105.9378),
    "South Carolina": ("Columbia", 34.0007, -81.0348),
    "Iowa": ("Des Moines", 41.5868, -93.6250),
    "Arkansas": ("Little Rock", 34.7465, -92.2896),
    "Kansas": ("Topeka", 39.0473, -95.6752),
}

FACTS = {
    "California": (38965193, 31), "Texas": (30503301, 28), "Florida": (22610726, 27),
    "New York": (19571216, 11), "Illinois": (12549689, 21), "Pennsylvania": (12961683, 2),
    "Ohio": (11785935, 17), "Michigan": (10037261, 26), "Georgia": (11029227, 4),
    "North Carolina": (10835491, 12), "Washington": (7812880, 42), "Arizona": (7431344, 48),
    "Colorado": (5877610, 38), "Montana": (1132812, 41), "Minnesota": (5737915, 32),
    "Missouri": (6196156, 24), "Tennessee": (7126489, 16), "Virginia": (8715698, 10),
    "Oregon": (4233358, 33), "Utah": (3417734, 45), "Nevada": (3194176, 36),
    "Louisiana": (4573749, 18), "Alabama": (5108468, 22), "Kentucky": (4526154, 15),
    "Maine": (1395722, 23), "New Mexico": (2114371, 47), "South Carolina": (5373555, 8),
    "Iowa": (3207004, 29), "Arkansas": (3067732, 25), "Kansas": (2940546, 34),
}

# Warm, distinct palette keyed to the playable set.
PALETTE = [
    "#e8a35c", "#d7765e", "#c95f7a", "#b76fa8", "#8a7ed6", "#6e93d6",
    "#5fa8c7", "#5fb9a6", "#79bd82", "#a5c46c", "#d0bb63", "#e0a45e",
    "#d98c5f", "#cf7d6c", "#c4708f", "#ab7ac0", "#8f83ce", "#7097c8",
    "#62aab6", "#66b79c", "#84b978", "#a9bd68", "#ccb769", "#dfa866",
    "#d89062", "#cb7d75", "#c07396", "#a87cba", "#8c86c7", "#6f9bc5",
]

WIDTH = 32.0
MARGIN = 0.0

def albers_projector():
    p1, p2, p0, l0 = map(math.radians, [29.5, 45.5, 37.5, -96.0])
    n = (math.sin(p1) + math.sin(p2)) / 2
    C = math.cos(p1) ** 2 + 2 * n * math.sin(p1)
    rho0 = math.sqrt(C - 2 * n * math.sin(p0)) / n

    def project(lon, lat):
        lam = math.radians(lon)
        phi = math.radians(lat)
        rho = math.sqrt(C - 2 * n * math.sin(phi)) / n
        theta = n * (lam - l0)
        return rho * math.sin(theta), rho0 - rho * math.cos(theta)

    return project


def ring_area(ring):
    area = 0.0
    for i in range(len(ring)):
        x1, y1 = ring[i]
        x2, y2 = ring[(i + 1) % len(ring)]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2


def rdp(points, epsilon):
    if len(points) < 3:
        return points
    start, end = points[0], points[-1]
    dx, dy = end[0] - start[0], end[1] - start[1]
    norm = math.hypot(dx, dy)
    best = -1.0
    index = 0
    for i in range(1, len(points) - 1):
        px, py = points[i]
        if norm == 0:
            dist = math.hypot(px - start[0], py - start[1])
        else:
            dist = abs(dy * px - dx * py + end[0] * start[1] - end[1] * start[0]) / norm
        if dist > best:
            best, index = dist, i
    if best > epsilon:
        left = rdp(points[: index + 1], epsilon)
        right = rdp(points[index:], epsilon)
        return left[:-1] + right
    return [start, end]


def simplify_ring(ring, epsilon):
    # Drop duplicate closing point and work in a circle-aware way.
    pts = ring[:-1] if ring[0] == ring[-1] else ring[:]
    if len(pts) < 4:
        return pts
    # Split the ring at its farthest-from-start point to avoid a degenerate chord.
    sx, sy = pts[0]
    far = max(range(len(pts)), key=lambda i: (pts[i][0] - sx) ** 2 + (pts[i][1] - sy) ** 2)
    a = rdp(pts[: far + 1], epsilon)
    b = rdp(pts[far:] + [pts[0]], epsilon)
    out = a[:-1] + b[:-1]
    return out


def main():
    raw = urllib.request.urlopen(SOURCE, timeout=30).read()
    data = json.loads(raw)
    project = albers_projector()

    # Establish common bounds over the 48 contiguous states.
    all_pts = []
    prepared = {}
    for feature in data["features"]:
        name = feature["properties"].get("name")
        if name in ("Alaska", "Hawaii", "District of Columbia", "Puerto Rico"):
            continue
        geom = feature["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        normalized = []
        for poly in polys:
            ring = [project(lon, lat) for lon, lat in poly[0]]
            normalized.append(ring)
            all_pts.extend(ring)
        prepared[name] = normalized

    xs = [p[0] for p in all_pts]
    ys = [p[1] for p in all_pts]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    scale = WIDTH / (max_x - min_x)
    height = (max_y - min_y) * scale

    def norm(pt):
        return ((pt[0] - min_x) * scale - WIDTH / 2,
                -(pt[1] - min_y) * scale + height / 2)

    def cap_points(name, epsilon, min_area, keep_largest=4):
        rings = []
        for ring in prepared[name]:
            projected = [norm(p) for p in ring]
            area = ring_area(projected)
            if area < min_area:
                continue
            simplified = simplify_ring(projected, epsilon)
            if len(simplified) >= 3:
                rings.append((area, simplified))
        rings.sort(reverse=True, key=lambda r: r[0])
        return [[[round(x, 2), round(z, 2)] for x, z in ring] for _, ring in rings[:keep_largest]]

    def centroid(ring):
        area = 0.0
        cx = 0.0
        cz = 0.0
        for i in range(len(ring)):
            x1, z1 = ring[i]
            x2, z2 = ring[(i + 1) % len(ring)]
            cross = x1 * z2 - x2 * z1
            area += cross
            cx += (x1 + x2) * cross
            cz += (z1 + z2) * cross
        area *= 0.5
        if abs(area) < 1e-6:
            return sum(p[0] for p in ring) / len(ring), sum(p[1] for p in ring) / len(ring)
        return cx / (6 * area), cz / (6 * area)

    states = []
    for i, name in enumerate(PLAYABLE):
        polys = cap_points(name, 0.11, 0.10, keep_largest=4)
        if not polys:
            raise RuntimeError("No geometry for " + name)
        cx, cz = centroid(polys[0])
        capital, lat, lon = CAPITAL_COORDS[name]
        cap_x, cap_z = norm(project(lon, lat))
        pop, order = FACTS[name]
        states.append({
            "id": ABBR[name],
            "name": name,
            "capital": capital,
            "population": pop,
            "order": order,
            "color": PALETTE[i],
            "center": [round(cx, 2), round(cz, 2)],
            "capitalPt": [round(cap_x, 2), round(cap_z, 2)],
            "polys": polys,
        })

    decor = []
    for name in sorted(prepared):
        if name in PLAYABLE:
            continue
        polys = cap_points(name, 0.18, 0.06, keep_largest=3)
        if polys:
            decor.append({"id": ABBR.get(name, name[:2]), "name": name, "polys": polys})

    payload = {"width": round(WIDTH, 2), "height": round(height, 2),
               "states": states, "decor": decor}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        fh.write("// Generated by tools/generate_map_data.py — public-domain US Census boundaries\n")
        fh.write("window.US_MAP_DATA = ")
        json.dump(payload, fh, separators=(",", ":"))
        fh.write(";\n")
    print(f"wrote {OUT}: {len(states)} states, {len(decor)} decor, height={height:.2f}, "
          f"size={os.path.getsize(OUT)} bytes")


if __name__ == "__main__":
    main()
