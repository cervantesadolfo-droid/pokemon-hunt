# Zeke's Pokémon QR Hunt

Birthday scavenger hunt with registration, a per-phone timer and a leaderboard for the host.

- Site root is served by GitHub Pages. Pages: `register.html` (door QR), `catch/<pokemon>.html` (hunt cards), `prize/…` (auto after 8 catches), `admin/…` (host leaderboard).
- `kit/build.py` regenerates the site and printables from one config block; `kit/coloring_book.py` builds the activity book. Run from `kit/`, then copy `kit/site/*` to the repo root.
- `kit/print/` has the door poster, hunt cards, Pokédex checklist and the host-only admin sheet.
