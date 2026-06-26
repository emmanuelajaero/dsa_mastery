#!/usr/bin/env python3
"""
One-shot build for DSA Mastery.

Run:
    python3 build.py

This regenerates everything from the Markdown source of truth, in order:
  1. build_game.py  -> the Pattern Forge game in  site/game/
  2. build_site.py  -> the study-guide site pages in  site/  (with Play buttons)

Re-run this whenever you edit the .md files (or the pattern registry).
No dependencies, fully offline.
"""
import pathlib

import build_game
import build_site

HERE = pathlib.Path(__file__).resolve().parent


def main():
    print("==> [1/2] Building the game (build_game.py)\n")
    build_game.main()

    print("\n==> [2/2] Building the site (build_site.py)\n")
    build_site.main()

    print("\nAll done. Open:", (HERE / "site" / "index.html"))
    print("Play directly:", (HERE / "site" / "game" / "index.html"))


if __name__ == "__main__":
    main()
