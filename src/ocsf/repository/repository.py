from dataclasses import dataclass
from typing import Generic, Optional, Iterable

from .helpers import RepoPath
from .definitions import ObjectDefn, DefinitionT, AnyDefinition


@dataclass
class DefinitionFile(Generic[DefinitionT]):
    path: str
    raw_data: Optional[str] = None
    data: Optional[DefinitionT] = None


class Repository:
    def __init__(self):
        self._contents: dict[RepoPath, DefinitionFile[AnyDefinition]] = {}

    def __getitem__(self, path: RepoPath) -> DefinitionFile[AnyDefinition]:
        return self._contents[path]

    def __delitem__(self, path: RepoPath) -> None:
        del self._contents[path]

    def __contains__(self, path: RepoPath) -> bool:
        return path in self._contents

    def __iter__(self) -> Iterable[str]:
        yield from self._contents.keys()

    def __len__(self) -> int:
        return len(self._contents)

    def __setitem__(self, path: RepoPath, file: DefinitionFile[AnyDefinition]) -> None:
        self._contents[path] = file
        # TODO: build reference of type short name, type short name + ext to path

    def object(self, name: str) -> list[DefinitionFile[ObjectDefn]]: ...
