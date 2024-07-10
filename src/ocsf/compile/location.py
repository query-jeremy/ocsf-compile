from dataclasses import dataclass
from abc import ABC
from pathlib import PurePath

from ocsf.repository import (
    RepoPath,
    Pathlike,
    path_defn_t,
    ObjectDefn,
    EventDefn,
    ProfileDefn,
    ExtensionDefn,
    DictionaryDefn,
)


class Location(ABC): ...


class DefnLocation(Location): ...


@dataclass(eq=True, frozen=True)
class FileLocation(Location):
    path: RepoPath

    def pure_path(self) -> PurePath:
        return PurePath(self.path)


@dataclass(eq=True, frozen=True)
class ObjectLocation(DefnLocation):
    name: str


@dataclass(eq=True, frozen=True)
class EventLocation(DefnLocation):
    name: str


@dataclass(eq=True, frozen=True)
class ProfileLocation(DefnLocation):
    name: str


@dataclass(eq=True, frozen=True)
class ExtensionLocation(DefnLocation):
    name: str


@dataclass(eq=True, frozen=True)
class DictionaryLocation(DefnLocation): ...


AnyDefnLocation = ObjectLocation | EventLocation | ProfileLocation | ExtensionLocation | DictionaryLocation
LocWithName = ObjectLocation | EventLocation | ProfileLocation | ExtensionLocation


def path_location_t(*path: Pathlike) -> type[AnyDefnLocation]:
    defn = path_defn_t(*path)
    if defn is ObjectDefn:
        return ObjectLocation
    elif defn is EventDefn:
        return EventLocation
    elif defn is ProfileDefn:
        return ProfileLocation
    elif defn is ExtensionDefn:
        return ExtensionLocation
    elif defn is DictionaryDefn:
        return DictionaryLocation
    else:
        raise ValueError(f"Unknown definition type at {path}")
