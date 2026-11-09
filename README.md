# PDF to DXF Converter

A simple Python script that converts a PDF layout into a DXF (CAD) file.

Useful when a client provides only a PDF drawing, but you need a CAD file for modelling or GIS work. The conversion runs on your own computer, so there is no website, login or upload.

## Requirements

- Python 3
- Two free libraries:

```
pip install pymupdf ezdxf
```

## How to use

1. Put `pdf_to_dxf.py` and your PDF in the same folder.
2. Open a terminal in that folder.
3. Run:

```
python pdf_to_dxf.py yourfile.pdf
```

The DXF file is saved in the same folder (for example, `yourfile_p1.dxf`).

## Options

| Option | Example | What it does |
|---|---|---|
| `--units` | `--units m` | Output units: `mm` (default), `m`, `in` |
| `--scale` | `--scale 100` | Drawing scale, e.g. 100 for a 1:100 drawing |
| `--pages` | `--pages 1 2` | Convert only these pages |
| `--no-text` | `--no-text` | Leave out text labels |

## Limitations

- Works only on PDFs exported from CAD or GIS software. Scanned drawings are images and will not convert.
- Circles and curves are made of short straight lines, not true arcs.
- Check the scale against a known dimension before using the drawing.

## License

MIT. Free to use and modify.
