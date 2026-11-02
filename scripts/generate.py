#!/usr/bin/env python3
"""Generate JetBrains icon assets and Kotlin mappings from vscode-symbols."""

from __future__ import annotations

import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

ROOT = Path(__file__).resolve().parent.parent

ICON_CATEGORIES = ('files', 'folders')
ICON_SIZE = 16


@dataclass(frozen=True)
class Config:
    theme_json: Path
    icons_src: Path
    icons_dest: Path
    kotlin_output: Path
    kotlin_package: str

    @classmethod
    def default(cls, root: Path = ROOT) -> Config:
        submodule = root / '_submodules/vscode-symbols/src'
        return cls(
            theme_json=submodule / 'symbol-icon-theme.json',
            icons_src=submodule / 'icons',
            icons_dest=root / 'src/main/resources/symbols/icons',
            kotlin_output=root / 'src/main/kotlin/com/github/sebastiandotdev/symbols/Icons.kt',
            kotlin_package='com.github.sebastiandotdev.symbols',
        )


@dataclass(frozen=True)
class Theme:
    icon_definitions: Mapping[str, str]  # icon name -> iconPath
    file_extensions: Mapping[str, str]
    file_names: Mapping[str, str]
    folder_names: Mapping[str, str]

    @classmethod
    def load(cls, path: Path) -> Theme:
        data = json.loads(path.read_text(encoding='utf-8'))
        return cls(
            icon_definitions={
                name: definition['iconPath']
                for name, definition in data['iconDefinitions'].items()
            },
            file_extensions=data['fileExtensions'],
            file_names=data['fileNames'],
            folder_names=data.get('folderNames') or {},
        )

    def is_valid_icon(self, icon: str) -> bool:
        return icon in self.icon_definitions

    def valid(self, mapping: Mapping[str, str]) -> dict[str, str]:
        return {key: icon for key, icon in mapping.items() if self.is_valid_icon(icon)}

    def orphans(self, *mappings: Mapping[str, str]) -> list[tuple[str, str]]:
        return [
            (key, icon)
            for mapping in mappings
            for key, icon in mapping.items()
            if not self.is_valid_icon(icon)
        ]


class SvgNormalizer:
    """Forces the root <svg> element to a fixed width/height."""

    _WIDTH = re.compile(r'\swidth="[^"]*"', re.IGNORECASE)
    _HEIGHT = re.compile(r'\sheight="[^"]*"', re.IGNORECASE)
    _HAS_WIDTH = re.compile(r' width="')
    _SVG_OPEN = re.compile(r'<svg([^>]*)>')

    def __init__(self, size: int = ICON_SIZE) -> None:
        self._size = size

    def normalize(self, content: str) -> str:
        normalized = self._WIDTH.sub(f' width="{self._size}"', content, count=1)
        normalized = self._HEIGHT.sub(f' height="{self._size}"', normalized, count=1)

        # Add width/height if the root <svg> element has neither
        if not self._HAS_WIDTH.search(normalized):
            normalized = self._SVG_OPEN.sub(
                rf'<svg\1 width="{self._size}" height="{self._size}">', normalized, count=1
            )

        return normalized

    def normalize_dir(self, directory: Path) -> None:
        for path in directory.glob('*.svg'):
            if not path.is_file():
                continue
            # Bytes I/O preserves the original line endings (e.g. CRLF)
            content = path.read_bytes().decode('utf-8')
            normalized = self.normalize(content)
            if normalized != content:
                path.write_bytes(normalized.encode('utf-8'))


class IconAssetSync:
    def __init__(self, src: Path, dest: Path, normalizer: SvgNormalizer) -> None:
        self._src = src
        self._dest = dest
        self._normalizer = normalizer

    def sync(self, categories: Iterable[str] = ICON_CATEGORIES) -> None:
        for category in categories:
            target = self._dest / category
            shutil.copytree(self._src / category, target, dirs_exist_ok=True)
            self._normalizer.normalize_dir(target)


def to_kt_field_name(name: str) -> str:
    # "angular-component" -> "angular_component", "react.ts" -> "react_ts"
    replaced = name.replace('-', '_').replace('.', '_')
    return f'_{replaced}' if replaced[:1].isdigit() else replaced


def lowercase_keys(mapping: Mapping[str, str]) -> dict[str, str]:
    # An exact lowercase key wins over a mixed-case one ("taskfile.yml" over "Taskfile.yml")
    result: dict[str, str] = {}
    for key, icon in mapping.items():
        lowered = key.lower()
        if lowered == key or lowered not in mapping:
            result[lowered] = icon
    return result


def icon_path_to_resource_path(icon_path: str) -> str:
    # "./icons/files/typescript.svg" -> "/symbols/icons/files/typescript.svg"
    return icon_path.replace('.', '/symbols', 1)


class KotlinIconsWriter:
    def __init__(self, package: str) -> None:
        self._package = package

    def render(self, theme: Theme) -> str:
        # Lookups lowercase the name, so keys must be lowercase too (e.g. "CLAUDE.md")
        return ''.join([
            self._header(),
            self._fields(theme.icon_definitions),
            self._map('EXT_TO_ICON', lowercase_keys(theme.valid(theme.file_extensions))),
            self._map('FOLDER_TO_ICON', lowercase_keys(theme.valid(theme.folder_names))),
            self._map('FILE_TO_ICON', lowercase_keys(theme.valid(theme.file_names))),
            '}\n',
        ])

    def _header(self) -> str:
        return (
            f'package {self._package}\n'
            '\n'
            'import com.intellij.openapi.util.IconLoader\n'
            'import javax.swing.Icon\n'
            '\n'
            'object Icons {\n'
        )

    @staticmethod
    def _fields(definitions: Mapping[str, str]) -> str:
        return ''.join(
            f'    @JvmField val {to_kt_field_name(name)}: Icon = '
            f'IconLoader.getIcon("{icon_path_to_resource_path(path)}", Icons::class.java)\n'
            for name, path in definitions.items()
        )

    @staticmethod
    def _map(name: str, entries: Mapping[str, str]) -> str:
        body = ''.join(
            f'        "{key}" to {to_kt_field_name(icon)},\n' for key, icon in entries.items()
        )
        return f'\n    val {name}: Map<String, Icon> = mapOf(\n{body}    )\n'


def warn_orphans(orphans: list[tuple[str, str]]) -> None:
    if not orphans:
        return
    print(f'⚠️  {len(orphans)} referencias sin SVG (ignoradas):', file=sys.stderr)
    for key, icon in orphans:
        print(f'   "{key}" → "{icon}"', file=sys.stderr)


def main(config: Config = Config.default()) -> None:
    theme = Theme.load(config.theme_json)

    warn_orphans(theme.orphans(theme.file_extensions, theme.file_names))

    IconAssetSync(config.icons_src, config.icons_dest, SvgNormalizer()).sync()
    print('SVGs copied successfully!')

    config.kotlin_output.write_text(
        KotlinIconsWriter(config.kotlin_package).render(theme), encoding='utf-8'
    )

    print('✅ Icons.kt generated successfully!')
    print(f'   → {len(theme.icon_definitions)} icons')
    print(f'   → {len(theme.file_extensions)} extensions')
    print(f'   → {len(theme.file_names)} file names')


if __name__ == '__main__':
    main()
