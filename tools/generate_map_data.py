#!/usr/bin/env python3
"""Build compact projected state geometry for the US Map Jigsaw game.

Source: PublicaMundi US states GeoJSON (public-domain boundaries derived from
the US Census Bureau). The 48 contiguous states are projected with an Albers
conic projection and normalized into the game's world units. Alaska and Hawaii
are projected separately and placed on a small Pacific inset board so the full
fifty-state atlas fits the tabletop layout.
"""
import json
import math
import os
import urllib.request

SOURCE = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "mapdata.js")

EXCLUDE = {"District of Columbia", "Puerto Rico"}

# All fifty states, alphabetical. The order also lays out the two trays.
STATE_NAMES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming",
]

ABBR = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
    "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
    "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
    "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
}

CAPITAL_COORDS = {
    "Alabama": ("Montgomery", 32.3668, -86.3000),
    "Alaska": ("Juneau", 58.3019, -134.4197),
    "Arizona": ("Phoenix", 33.4484, -112.0740),
    "Arkansas": ("Little Rock", 34.7465, -92.2896),
    "California": ("Sacramento", 38.5816, -121.4944),
    "Colorado": ("Denver", 39.7392, -104.9903),
    "Connecticut": ("Hartford", 41.7658, -72.6734),
    "Delaware": ("Dover", 39.1582, -75.5244),
    "Florida": ("Tallahassee", 30.4383, -84.2807),
    "Georgia": ("Atlanta", 33.7490, -84.3880),
    "Hawaii": ("Honolulu", 21.3069, -157.8583),
    "Idaho": ("Boise", 43.6150, -116.2023),
    "Illinois": ("Springfield", 39.7817, -89.6501),
    "Indiana": ("Indianapolis", 39.7684, -86.1581),
    "Iowa": ("Des Moines", 41.5868, -93.6250),
    "Kansas": ("Topeka", 39.0473, -95.6752),
    "Kentucky": ("Frankfort", 38.2009, -84.8733),
    "Louisiana": ("Baton Rouge", 30.4515, -91.1871),
    "Maine": ("Augusta", 44.3106, -69.7795),
    "Maryland": ("Annapolis", 38.9784, -76.4922),
    "Massachusetts": ("Boston", 42.3601, -71.0589),
    "Michigan": ("Lansing", 42.7325, -84.5555),
    "Minnesota": ("Saint Paul", 44.9537, -93.0900),
    "Mississippi": ("Jackson", 32.2988, -90.1848),
    "Missouri": ("Jefferson City", 38.5767, -92.1735),
    "Montana": ("Helena", 46.5891, -112.0391),
    "Nebraska": ("Lincoln", 40.8136, -96.7026),
    "Nevada": ("Carson City", 39.1638, -119.7674),
    "New Hampshire": ("Concord", 43.2081, -71.5376),
    "New Jersey": ("Trenton", 40.2171, -74.7429),
    "New Mexico": ("Santa Fe", 35.6870, -105.9378),
    "New York": ("Albany", 42.6526, -73.7562),
    "North Carolina": ("Raleigh", 35.7796, -78.6382),
    "North Dakota": ("Bismarck", 46.8083, -100.7837),
    "Ohio": ("Columbus", 39.9612, -82.9988),
    "Oklahoma": ("Oklahoma City", 35.4676, -97.5164),
    "Oregon": ("Salem", 44.9429, -123.0351),
    "Pennsylvania": ("Harrisburg", 40.2732, -76.8867),
    "Rhode Island": ("Providence", 41.8240, -71.4128),
    "South Carolina": ("Columbia", 34.0007, -81.0348),
    "South Dakota": ("Pierre", 44.3683, -100.3510),
    "Tennessee": ("Nashville", 36.1627, -86.7816),
    "Texas": ("Austin", 30.2672, -97.7431),
    "Utah": ("Salt Lake City", 40.7608, -111.8910),
    "Vermont": ("Montpelier", 44.2601, -72.5754),
    "Virginia": ("Richmond", 37.5407, -77.4360),
    "Washington": ("Olympia", 47.0379, -122.9007),
    "West Virginia": ("Charleston", 38.3498, -81.6326),
    "Wisconsin": ("Madison", 43.0731, -89.4012),
    "Wyoming": ("Cheyenne", 41.1400, -104.8202),
}

FACTS = {
    "Alabama": (5108468, 22), "Alaska": (733406, 49), "Arizona": (7431344, 48),
    "Arkansas": (3067732, 25), "California": (38965193, 31),
    "Colorado": (5877610, 38), "Connecticut": (3617176, 5),
    "Delaware": (1031890, 1), "Florida": (22610726, 27),
    "Georgia": (11029227, 4), "Hawaii": (1435138, 50), "Idaho": (1964726, 43),
    "Illinois": (12549689, 21), "Indiana": (6862199, 19), "Iowa": (3207004, 29),
    "Kansas": (2940546, 34), "Kentucky": (4526154, 15),
    "Louisiana": (4573749, 18), "Maine": (1395722, 23),
    "Maryland": (6180253, 7), "Massachusetts": (7001399, 6),
    "Michigan": (10037261, 26), "Minnesota": (5737915, 32),
    "Mississippi": (2939690, 20), "Missouri": (6196156, 24),
    "Montana": (1132812, 41), "Nebraska": (1978379, 37),
    "Nevada": (3194176, 36), "New Hampshire": (1402054, 9),
    "New Jersey": (9290841, 3), "New Mexico": (2114371, 47),
    "New York": (19571216, 11), "North Carolina": (10835491, 12),
    "North Dakota": (783926, 39), "Ohio": (11785935, 17),
    "Oklahoma": (4053824, 46), "Oregon": (4233358, 33),
    "Pennsylvania": (12961683, 2), "Rhode Island": (1095962, 13),
    "South Carolina": (5373555, 8), "South Dakota": (919318, 40),
    "Tennessee": (7126489, 16), "Texas": (30503301, 28), "Utah": (3417734, 45),
    "Vermont": (647464, 14), "Virginia": (8715698, 10),
    "Washington": (7812880, 42), "West Virginia": (1770071, 35),
    "Wisconsin": (5910955, 30), "Wyoming": (584057, 44),
}

# Inset board and the two local projection boxes, in game world units.
INSET = {
    "board": {"cx": 24.8, "cz": 17.0, "w": 11.6, "d": 10.2},
    "alaska": {"cx": 24.8, "cz": 14.85, "w": 6.8, "h": 4.8, "lat0": 64.0},
    "hawaii": {"cx": 24.8, "cz": 19.65, "w": 4.2, "h": 2.2, "lat0": 20.6},
}

WIDTH = 32.0


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
    pts = ring[:-1] if ring[0] == ring[-1] else ring[:]
    if len(pts) < 4:
        return pts
    sx, sy = pts[0]
    far = max(range(len(pts)), key=lambda i: (pts[i][0] - sx) ** 2 + (pts[i][1] - sy) ** 2)
    a = rdp(pts[: far + 1], epsilon)
    b = rdp(pts[far:] + [pts[0]], epsilon)
    return a[:-1] + b[:-1]


def inset_projector(lat0):
    c = math.cos(math.radians(lat0))
    return lambda lon, lat: (lon * c, -lat)


def fit_rings(rings, box, epsilon, min_area, max_rings=7):
    """Project lon/lat rings into a local inset box, preserving aspect."""
    project = inset_projector(box["lat0"])
    projected = []
    for ring in rings:
        pts = [project(lon, lat) for lon, lat in ring]
        projected.append(pts)
    xs = [x for ring in projected for x, z in ring]
    zs = [z for ring in projected for x, z in ring]
    minx, maxx = min(xs), max(xs)
    minz, maxz = min(zs), max(zs)
    scale = min(box["w"] / max(1e-9, maxx - minx), box["h"] / max(1e-9, maxz - minz))
    ox = box["cx"] - (minx + maxx) * scale / 2
    oz = box["cz"] - (minz + maxz) * scale / 2

    def to_world(pt):
        return (ox + pt[0] * scale, oz + pt[1] * scale)

    out = []
    for ring in projected:
        world = [to_world(p) for p in ring]
        area = ring_area(world)
        if area < min_area:
            continue
        simp = simplify_ring(world, epsilon)
        if len(simp) >= 3:
            out.append((area, simp))
    out.sort(reverse=True, key=lambda r: r[0])
    return [[[round(x, 2), round(z, 2)] for x, z in ring] for _, ring in out[:max_rings]], to_world




def point_in_ring(x, z, ring):
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, zi = ring[i]
        xj, zj = ring[j]
        if ((zi > z) != (zj > z)) and (x < (xj - xi) * (z - zi) / (zj - zi) + xi):
            inside = not inside
        j = i
    return inside


def point_in_polys(x, z, polys):
    return any(point_in_ring(x, z, ring) for ring in polys)


def nudge_inside(polys, x, z, step=0.05):
    """If a capital projects just offshore, find the closest on-land point."""
    if point_in_polys(x, z, polys):
        return x, z
    xs = [p[0] for ring in polys for p in ring]
    zs = [p[1] for ring in polys for p in ring]
    best = None
    best_d = float('inf')
    gx = min(xs)
    while gx <= max(xs) + 1e-9:
        gz = min(zs)
        while gz <= max(zs) + 1e-9:
            if point_in_polys(gx, gz, polys):
                d = (gx - x) ** 2 + (gz - z) ** 2
                if d < best_d:
                    best_d = d
                    best = (gx, gz)
            gz += step
        gx += step
    return best if best else (x, z)


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


def palette(count):
    colors = []
    for i in range(count):
        hue = (18 + i * 137.508) % 360
        sat = 0.46 + (i % 4) * 0.035
        light = 0.59 + (i % 3) * 0.045
        # HSL -> CSS hex
        h = hue / 360.0
        q = light * (1 + sat) if light < 0.5 else light + sat - light * sat
        p = 2 * light - q
        def hue2rgb(t):
            t = t % 1
            if t < 1 / 6: return p + (q - p) * 6 * t
            if t < 1 / 2: return q
            if t < 2 / 3: return p + (q - p) * (2 / 3 - t) * 6
            return p
        r = round(hue2rgb(h + 1 / 3) * 255)
        g = round(hue2rgb(h) * 255)
        b = round(hue2rgb(h - 1 / 3) * 255)
        colors.append(f"#{r:02x}{g:02x}{b:02x}")
    return colors


def main():
    raw = urllib.request.urlopen(SOURCE, timeout=30).read()
    data = json.loads(raw)
    project = albers_projector()

    raw_polys = {}
    for feature in data["features"]:
        name = feature["properties"].get("name")
        if name in EXCLUDE or name not in STATE_NAMES:
            continue
        geom = feature["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        raw_polys[name] = [poly[0] for poly in polys]

    # Common bounds for the 48 contiguous states.
    contiguous_pts = []
    for name, polys in raw_polys.items():
        if name in ("Alaska", "Hawaii"):
            continue
        for ring in polys:
            contiguous_pts.extend(project(lon, lat) for lon, lat in ring)
    xs = [p[0] for p in contiguous_pts]
    ys = [p[1] for p in contiguous_pts]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    scale = WIDTH / (max_x - min_x)
    height = (max_y - min_y) * scale

    def norm(pt):
        return ((pt[0] - min_x) * scale - WIDTH / 2,
                -(pt[1] - min_y) * scale + height / 2)

    def contiguous_shapes(name, epsilon, min_area, keep_largest=8):
        rings = []
        for ring in raw_polys[name]:
            projected = [norm(project(lon, lat)) for lon, lat in ring]
            area = ring_area(projected)
            if area < min_area:
                continue
            simplified = simplify_ring(projected, epsilon)
            if len(simplified) >= 3:
                rings.append((area, simplified))
        rings.sort(reverse=True, key=lambda r: r[0])
        return [[[round(x, 2), round(z, 2)] for x, z in ring] for _, ring in rings[:keep_largest]]

    colors = palette(len(STATE_NAMES))
    states = []
    for idx, name in enumerate(STATE_NAMES):
        capital, lat, lon = CAPITAL_COORDS[name]
        pop, order = FACTS[name]
        if name == "Alaska":
            polys, to_world = fit_rings(raw_polys[name], INSET["alaska"], 0.08, 0.05, 7)
            cap_x, cap_z = to_world(inset_projector(INSET["alaska"]["lat0"])(lon, lat))
            inset = "alaska"
        elif name == "Hawaii":
            polys, to_world = fit_rings(raw_polys[name], INSET["hawaii"], 0.045, 0.015, 6)
            cap_x, cap_z = to_world(inset_projector(INSET["hawaii"]["lat0"])(lon, lat))
            inset = "hawaii"
        else:
            polys = contiguous_shapes(name, 0.11, 0.08 if name not in ("Rhode Island", "Delaware") else 0.015)
            cap_x, cap_z = norm(project(lon, lat))
            inset = None
        if not polys:
            raise RuntimeError("No geometry for " + name)
        cap_x, cap_z = nudge_inside(polys, cap_x, cap_z)
        cx, cz = centroid(polys[0])
        states.append({
            "id": ABBR[name],
            "name": name,
            "capital": capital,
            "population": pop,
            "order": order,
            "color": colors[idx],
            "center": [round(cx, 2), round(cz, 2)],
            "capitalPt": [round(cap_x, 2), round(cap_z, 2)],
            "polys": polys,
            "inset": inset,
        })

    payload = {
        "width": round(WIDTH, 2),
        "height": round(height, 2),
        "states": states,
        "decor": [],
        "insets": INSET,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        fh.write("// Generated by tools/generate_map_data.py — public-domain US Census boundaries\n")
        fh.write("window.US_MAP_DATA = ")
        json.dump(payload, fh, separators=(",", ":"))
        fh.write(";\n")
    print(f"wrote {OUT}: {len(states)} states, height={height:.2f}, size={os.path.getsize(OUT)} bytes")
    for st in states:
        if st["inset"]:
            xs = [x for poly in st["polys"] for x, z in poly]
            zs = [z for poly in st["polys"] for x, z in poly]
            print(f"  {st['id']} inset={st['inset']} polys={len(st['polys'])} bbox=({min(xs):.2f},{max(xs):.2f}) x ({min(zs):.2f},{max(zs):.2f}) cap={st['capitalPt']}")


if __name__ == "__main__":
    main()
