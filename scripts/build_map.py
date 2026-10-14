#!/usr/bin/env python3
"""Build the local Equal Earth land outline from Natural Earth 110m GeoJSON.

Usage: python3 scripts/build_map.py /path/to/ne_110m_land.geojson
No packages or network requests are needed by this script or by the website.
"""

import json
import math
from pathlib import Path
import sys


def project(longitude, latitude):
    """Return x, y in the personal map's 1000 × 500 SVG coordinate system."""
    theta = math.asin(math.sqrt(3) / 2 * math.sin(math.radians(latitude)))
    polynomial = 1.340264 - 0.081106 * theta**2 + 0.000893 * theta**6 + 0.003796 * theta**8
    derivative = 1.340264 - 3 * 0.081106 * theta**2 + 7 * 0.000893 * theta**6 + 9 * 0.003796 * theta**8
    x = 2 * math.radians(longitude) * math.cos(theta) / (math.sqrt(3) * derivative)
    y = theta * polynomial
    return (500 + 175 * x, 250 - 175 * y)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    source = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    paths = []
    for feature in source["features"]:
        geometry = feature["geometry"]
        if geometry["type"] == "Polygon":
            polygons = [geometry["coordinates"]]
        elif geometry["type"] == "MultiPolygon":
            polygons = geometry["coordinates"]
        else:
            raise ValueError("Expected land polygons")
        for polygon in polygons:
            rings = []
            for ring in polygon:
                points = [project(lon, lat) for lon, lat in ring]
                rings.append("M" + "L".join("{:.1f},{:.1f}".format(x, y) for x, y in points) + "Z")
            paths.append('    <path d="{}"/>'.format("".join(rings)))
    output = Path(__file__).resolve().parents[1] / "site/assets/world-land.svg"
    output.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 500">\n'
        '  <!-- Natural Earth 110m land, public domain: https://www.naturalearthdata.com/ -->\n'
        '  <!-- Equal Earth projection; regenerate with scripts/build_map.py. -->\n'
        '  <g id="land" fill-rule="evenodd">\n'
        + "\n".join(paths)
        + '\n  </g>\n</svg>\n',
        encoding="utf-8",
    )
    print("Wrote {} land polygons to {}".format(len(paths), output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
