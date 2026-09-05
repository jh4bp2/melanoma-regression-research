from dataclasses import dataclass
from pathlib import Path


PROMPTS_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class PromptTemplate:
    name: str
    version: str
    content: str


def load_prompt(name: str, version: str = "v1") -> PromptTemplate:
    path = PROMPTS_DIR / f"{name}_{version}.txt"
    if not path.is_file():
        raise FileNotFoundError(f"Prompt not found: {path.name}")
    return PromptTemplate(
        name=name,
        version=version,
        content=path.read_text(encoding="utf-8"),
    )
