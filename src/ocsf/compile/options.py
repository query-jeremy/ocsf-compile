from dataclasses import dataclass
from typing import Optional


@dataclass
class CompilationOptions:
    profiles: Optional[list[str]] = None
    extensions: Optional[list[str]] = None
    ignore_profiles: Optional[list[str]] = None
    ignore_extensions: Optional[list[str]] = None
