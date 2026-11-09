# PDF to DXF converter
# Converts PDF site layouts to DXF so they can be used in CAD / GIS / modelling.
# Works only for vector PDFs (exported from CAD), not scanned drawings.
#
# pip install pymupdf ezdxf
# python pdf_to_dxf.py layout.pdf --scale 100

import os
import argparse
import ezdxf
import pymupdf


# pdf points to mm / m / inch
units = {"mm": 25.4 / 72, "m": 0.0254 / 72, "in": 1 / 72}
dxf_units = {"mm": 4, "m": 6, "in": 1}


def curve_to_points(p0, p1, p2, p3, n=16):
    # break the bezier curve into small straight lines
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1-t)**3*p0[0] + 3*(1-t)**2*t*p1[0] + 3*(1-t)*t**2*p2[0] + t**3*p3[0]
        y = (1-t)**3*p0[1] + 3*(1-t)**2*t*p1[1] + 3*(1-t)*t**2*p2[1] + t**3*p3[1]
        pts.append((x, y))
    return pts


def convert_page(page, msp, f, text=True):
    h = page.rect.height

    def xy(p):
        # pdf y axis goes down, cad y axis goes up
        return (p.x * f, (h - p.y) * f)

    n = 0
    for path in page.get_drawings():
        pts = []
        for item in path["items"]:
            if item[0] == "l":
                a, b = xy(item[1]), xy(item[2])
                if pts and pts[-1] != a:
                    msp.add_lwpolyline(pts, dxfattribs={"layer": "LINES"})
                    n += 1
                    pts = []
                if not pts:
                    pts.append(a)
                pts.append(b)

            elif item[0] == "c":
                c = curve_to_points(*[xy(p) for p in item[1:5]])
                if pts and pts[-1] != c[0]:
                    msp.add_lwpolyline(pts, dxfattribs={"layer": "LINES"})
                    n += 1
                    pts = []
                if not pts:
                    pts.append(c[0])
                pts += c[1:]

            elif item[0] == "re":
                r = item[1]
                box = [xy(r.tl), xy(r.tr), xy(r.br), xy(r.bl)]
                msp.add_lwpolyline(box, close=True, dxfattribs={"layer": "LINES"})
                n += 1

            elif item[0] == "qu":
                q = item[1]
                box = [xy(q.ul), xy(q.ur), xy(q.lr), xy(q.ll)]
                msp.add_lwpolyline(box, close=True, dxfattribs={"layer": "LINES"})
                n += 1

        if len(pts) > 1:
            msp.add_lwpolyline(pts, close=path.get("closePath", False),
                               dxfattribs={"layer": "LINES"})
            n += 1

    if text:
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    if span["text"].strip():
                        x, y = xy(pymupdf.Point(span["origin"]))
                        msp.add_text(span["text"].strip(),
                                     height=span["size"] * f * 0.75,
                                     dxfattribs={"layer": "TEXT", "insert": (x, y)})
                        n += 1
    return n


parser = argparse.ArgumentParser()
parser.add_argument("pdf")
parser.add_argument("--units", default="mm", choices=units)
parser.add_argument("--scale", type=float, default=1, help="eg. 100 for 1:100 drawing")
parser.add_argument("--pages", nargs="+", type=int, help="page numbers, default all")
parser.add_argument("--no-text", action="store_true")
args = parser.parse_args()

pdf = pymupdf.open(args.pdf)
f = units[args.units] * args.scale
name = os.path.splitext(args.pdf)[0]
pages = args.pages if args.pages else range(1, len(pdf) + 1)

for p in pages:
    dxf = ezdxf.new("R2010")
    dxf.header["$INSUNITS"] = dxf_units[args.units]
    n = convert_page(pdf[p - 1], dxf.modelspace(), f, not args.no_text)
    out = f"{name}_p{p}.dxf"
    dxf.saveas(out)
    print(f"page {p}: {n} objects -> {out}")
