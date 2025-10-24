from __future__ import annotations

import re
from typing import Sequence

__all__ = ["extract_quantity"]


def extract_quantity(command: str, aliases: Sequence[str]) -> int:
    """Extrai quantidade de um comando textual."""
    lowered = command.lower()
    for alias in aliases:
        if not alias:
            continue
        pattern = re.compile(rf"(\d+)[^a-zA-Z0-9]+(?:de\s+)?{re.escape(alias.lower())}")
        match = pattern.search(lowered)
        if match:
            return int(match.group(1))
    generic = re.search(r"(\d+)", lowered)
    return int(generic.group(1)) if generic else 1
