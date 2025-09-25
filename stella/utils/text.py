from __future__ import annotations

import re

__all__ = ["normalize_key"]


_NORM_PATTERN = re.compile(r"[\s,.:;/\\]+")


def normalize_key(value: str | None) -> str:
    """Normaliza nomes de produtos para comparação consistente."""
    if not value:
        return ""
    return _NORM_PATTERN.sub("_", value.strip().lower()).strip("_")
