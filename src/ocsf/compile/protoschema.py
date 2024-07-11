import dacite

from copy import deepcopy
from dataclasses import asdict
from typing import Any, cast

from ocsf.schema import OcsfSchema, OcsfObject, OcsfEvent
from ocsf.repository import (
    Repository,
    ObjectDefn,
    EventDefn,
    ExtensionDefn,
    ProfileDefn,
    DictionaryDefn,
    AnyDefinition,
    DefinitionFile,
    RepoPath,
    RepoPaths,
    as_path,
    extension,
)


def _remove_nones(data: dict[str, Any]) -> None:
    rm: list[str] = []
    for k, v in data.items():
        if v is None:
            rm.append(k)
        elif isinstance(v, dict):
            v = cast(dict[str, Any], v)
            # No need to update data[k] b/c v is a reference to data[k]
            _remove_nones(v)

    for k in rm:
        del data[k]


class ProtoSchema:
    def __init__(self, repo: Repository):
        self.repo = repo
        self._files: dict[RepoPath, DefinitionFile] = {}

    def __getitem__(self, path: RepoPath) -> DefinitionFile:
        if path not in self._files:
            if path in self.repo:
                self._files[path] = deepcopy(self.repo[path])
            else:
                raise KeyError(f"File {path} not found in repository")
        return self._files[path]

    def __setitem__(self, path: RepoPath, file: DefinitionFile) -> None:
        # value = deepcopy(value)
        file.path = path
        self._files[path] = file

    def object_path(self, name: str) -> RepoPath:
        return as_path(RepoPaths.OBJECTS.value, name, ".json")

    def event_path(self, name: str) -> RepoPath:
        default = as_path(RepoPaths.EVENTS.value, name, ".json")
        if default not in self.repo:
            for file in self.repo.files():
                if file.path.startswith(RepoPaths.EVENTS.value):
                    if file.short_name() == name:
                        return file.path
        return default

    def profile_path(self, name: str) -> RepoPath:
        return as_path(RepoPaths.PROFILES.value, name, ".json")

    def schema(self) -> OcsfSchema:
        schema = OcsfSchema(version="0.0.0")  # TODO implement version

        for file in self._files.values():
            try:
                if file.path.startswith(RepoPaths.OBJECTS.value) and not extension(file.path):
                    assert file.data is not None
                    assert isinstance(file.data, ObjectDefn)
                    assert file.data.name is not None
                    data = asdict(file.data)
                    _remove_nones(data)

                    schema.objects[file.data.name] = dacite.from_dict(OcsfObject, data)

                elif file.path.startswith(RepoPaths.EVENTS.value):
                    assert file.data is not None
                    assert isinstance(file.data, EventDefn)
                    assert file.data.name is not None
                    data = asdict(file.data)
                    _remove_nones(data)

                    schema.classes[file.data.name] = dacite.from_dict(OcsfEvent, data)

            except Exception as e:
                from pprint import pprint

                pprint(file.data)
                raise ValueError(f"Error processing {file.path}: {e}") from e

        if "base" in schema.classes:
            schema.base_event = schema.classes["base"]

        return schema
