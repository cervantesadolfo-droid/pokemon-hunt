# Pokémon QR Hunt

Birthday-party scavenger hunt. Each hidden card has a QR code that opens a page in `catch/`;
the secret letters spell where the Master Ball (prize) card is hidden, which opens `prize/`.

- Site is served from the repo root via GitHub Pages.
- `kit/build.py` regenerates the site and printables from one config block. Run it from `kit/`
  after changing images, then copy `kit/site/*` to the repo root.
- `kit/print/` has the hunt cards, Pokédex sheet and parent cheat sheet.
