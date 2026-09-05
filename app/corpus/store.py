from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.core.config import PROJECT_ROOT


def default_corpus_root() -> Path:
    return PROJECT_ROOT / "data" / "corpus"


class CorpusStore:
    def __init__(self, root: Path | None = None):
        self.root = Path(root) if root is not None else default_corpus_root()
        self.history_dir = self.root / "history"

    def ensure(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def path(self, name: str) -> Path:
        return self.root / name

    def read_json(self, name: str, default: Any) -> Any:
        path = self.path(name)
        if not path.is_file():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def write_json(self, name: str, payload: Any, *, snapshot: bool = True) -> Path:
        self.ensure()
        path = self.path(name)
        if snapshot and path.is_file():
            stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
            archive = self.history_dir / f"{path.stem}_{stamp}{path.suffix}"
            shutil.copy2(path, archive)
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return path

    def history_files(self, stem: str) -> list[Path]:
        if not self.history_dir.is_dir():
            return []
        return sorted(self.history_dir.glob(f"{stem}_*{Path(stem).suffix or '.json'}"))
