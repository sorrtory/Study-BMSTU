# Mermaid

## ER

use invicible char

## config

`mermaid-config.json` for options that helps to preserve text

## Convert to PNG

```bash
mmdc -i diagram.mmd -o diagram.png -b transparent \
  -s 3 -w 2400 -H 1600 \
  -c <(printf '%s' '{"htmlLabels":false,"fontFamily":"Arial, sans-serif"}')

```

### SVG -> PNG with Inkscape
```bash
inkscape mdb.svg \                                            
  --export-type=png \
  --export-filename=diagram@highres.png \
  --export-width=3840 \
  --export-background-opacity=0
```

## Convert to SVG

```bash
npm install -g @mermaid-js/mermaid-cli
vim diagram.mmd

mmdc -i diagram.mmd -o diagram.svg -b transparent \
  -c <(printf '%s' '{"htmlLabels":false,"fontFamily":"Arial, sans-serif"}')
```

## Convert to pdf

```bash
vim diagram.mmd

mmdc -i diagram.mmd -o diagram.pdf \
  -b transparent \
  -f \
  -w 2400 \
  -H 1600 \
  -c <(printf '%s' '{"htmlLabels":false,"fontFamily":"Arial, sans-serif"}')
```
