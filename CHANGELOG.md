<!-- Keep a Changelog guide -> https://keepachangelog.com -->

# symbols Changelog

## [Unreleased]

### Added

- Modules, module groups, packages and content roots in the Project view now use theme icons.

### Changed

- Migrated the icon generator from TypeScript to Python (`scripts/generate.py`), managed with `uv`.

### Fixed

- File names and extensions with mixed case in the theme (e.g. `CLAUDE.md`, `CNAME`, `Caddyfile`) now resolve to their icons.

## [0.2.0]

### Fixed

- Folder color icons now render correctly for named folders (`src`, `test`, `tests`, `docs`, `components`, `pages`, `styles`, `scripts`, `types`, `dist`, `.github`, `.git`, `node_modules`, and 140+ more). The generator was reading icon definition keys instead of `folderNames` from the theme, so color-coded folders were silently ignored.
- Fixed `biome.svg` and `swc.svg` rendering at 48px instead of 16px due to missing `width`/`height` attributes on their root `<svg>` element.
- Icon generator (`generate.ts`) now injects `width="16" height="16"` on any SVG that lacks those attributes entirely, not only SVGs that already have them with a different value.

## [0.1.2] - 2026-04-08

For stable releases, please refer to [CHANGELOG.md](https://github.com/joansgarcia/jetbrains-symbols/blob/main/CHANGELOG.md) for details.

## [0.1.1] - 2026-04-08

### Fixed

- Updated platform target to IntelliJ 2026.1 for full compatibility.
- Lowered `since-build` to 241 (IntelliJ 2024.1+) for broader IDE support.

## [0.1.0] - 2026-04-07

### Added

- Initial public release of Symbols Icons for JetBrains.
- File and folder icon provider with generated mappings from `vscode-symbols`.
- Automated icon generation pipeline using `deno task build`.
- Icon-provider integration tests covering filename, extension, folder, and fallback behavior.

### Changed

- Normalized generated SVG dimensions for JetBrains tree rendering.
- CI release guards to fail when generated icon assets are out of sync.

[Unreleased]: https://github.com/joansgarcia/jetbrains-symbols/compare/0.2.0...HEAD
[0.2.0]: https://github.com/joansgarcia/jetbrains-symbols/compare/0.1.2...0.2.0
[0.1.2]: https://github.com/joansgarcia/jetbrains-symbols/compare/0.1.1...0.1.2
[0.1.1]: https://github.com/joansgarcia/jetbrains-symbols/compare/0.1.0...0.1.1
[0.1.0]: https://github.com/joansgarcia/jetbrains-symbols/commits/0.1.0
