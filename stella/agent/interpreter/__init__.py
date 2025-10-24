"""Interpretadores de comandos Stella."""

from .base import AbstractInterpreter
from .factory import get_interpreter

__all__ = ["AbstractInterpreter", "get_interpreter"]
