from dataclasses import dataclass
from pathlib import PurePath
from typing import Optional, Iterable

from .helpers import RepoPath, RepoPaths
from .definitions import AnyDefinition


@dataclass
class DefinitionFile:
    path: RepoPath
    raw_data: Optional[str] = None
    data: Optional[AnyDefinition] = None

    def short_name(self) -> str:
        return PurePath(self.path).stem


class Repository:
    def __init__(self, contents: Optional[dict[RepoPath, DefinitionFile]] = None):
        if contents is not None:
            self._contents = contents
        else:
            self._contents: dict[RepoPath, DefinitionFile] = {}

    def __getitem__(self, path: RepoPath) -> DefinitionFile:
        return self._contents[path]

    def __delitem__(self, path: RepoPath) -> None:
        del self._contents[path]

    def __contains__(self, path: RepoPath) -> bool:
        return path in self._contents

    def __len__(self) -> int:
        return len(self._contents)

    def __setitem__(self, path: RepoPath, file: DefinitionFile) -> None:
        file.path = path
        self._contents[path] = file

    def files(self) -> Iterable[DefinitionFile]:
        yield from self._contents.values()

    def paths(self) -> Iterable[RepoPath]:
        yield from self._contents.keys()

    def extensions(self) -> Iterable[str]:
        extns: set[str] = set()
        for path in self._contents:
            if path.startswith(RepoPaths.EXTENSIONS.value):
                extns.add(PurePath(path).parts[1])
        yield from extns

    def profiles(self) -> Iterable[str]:
        # TODO include profiles from extensions
        for path in self._contents:
            if path.startswith(RepoPaths.PROFILES.value):
                yield PurePath(path).stem
