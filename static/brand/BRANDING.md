# RentCarKom logo

The mark is a charcoal tile with an orange R. A short curve under the tile suggests a road. The wordmark is two text nodes: `RentCar` and `Kom`.

## Files

| File | Use |
|---|---|
| `logo.svg` | Main horizontal logo for light backgrounds |
| `logo-light.svg` | Same lockup, shown when the site theme is light |
| `logo-dark.svg` | Light wordmark for the dark theme |
| `logo-mark.svg` | Icon only |
| `favicon.svg` | Browser tab icon |

The header in `templates/base.html` loads `logo-light.svg` and `logo-dark.svg`. CSS hides the one that does not match `data-theme` on `<html>`.

## Replace the logo

1. Edit the SVG files in this folder. Keep the mark and the two `<text>` nodes separate.
2. To change the name, edit the text inside those nodes. `Kom` stays the orange accent.
3. Save the files. Refresh the site. The templates point at these files, so no Python change is required.
4. If the browser keeps the old icon, bump the `?v=` query on the logo and favicon links in `templates/base.html`.

Do not draw the logo into car photos or page backgrounds. Swap only these SVG files.
