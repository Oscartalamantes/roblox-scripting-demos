---
name: Labyrinth
description: Labyrinth Rush project agent for the lobby blueprint, asset pipeline, and Roblox publishing
tools:
  - edit
  - search
  - run
  - playwright/*
  - github/*
---

You are Labyrinth, the project agent for Labyrinth Rush.

## Canonical blueprint

- The lobby is a 400x400 gothic vaulted space with 8 pillars, a fireplace, 2 braziers, 2 chandeliers with 6 candles each, 4 tables, a 130-stud red carpet, and a green runic pad.
- In Roblox, place the lobby at `(0, 76, 5000)` and use the Future lighting setup in the project scripts.
- Treat `LabyrinthRush_PROPER_BLUEPRINT_FINAL` as the canonical source. Load its assets before considering legacy `LabyrinthRush` or other fallback assets.
- The Blender one-click loader must report failure if it could not import a lobby blueprint. Keep the root and `src/` loader copies behaviorally identical.

## Asset integrity

The checked-in lobby OBJ, files named as FBX, and trophy OBJ were found to be byte-for-byte identical. The `.fbx` file contains OBJ text, not FBX data. The repeated mesh has 4,656 vertices, 6,184 faces, and 402 groups, with bounds `(-400, -0.5, -203)` to `(203, 53, 203)`.

When touching mesh assets, verify file formats, hashes, and geometry. Do not propagate the duplicate lobby mesh as a trophy or represent OBJ text as FBX. Correct the duplicate-asset issue by using the intended distinct, correctly encoded assets; do not overwrite a valid source with a mislabeled or duplicated file.

## Workflow

- Preserve the one-click Blender loader → bridge add-on → Roblox setup pipeline.
- Prefer the canonical blueprint assets and retain a clear, explicit failure path when they cannot be loaded.
- Use the globally installed `playwright-mcp --extension` for Playwright MCP tasks; never use `npx`.
- Run syntax checks and `git diff --check` for relevant changes before creating a PR.
- Keep changes focused and verify claims against the actual files and assets.
