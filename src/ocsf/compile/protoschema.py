import dacite

from copy import deepcopy
from dataclasses import asdict
from typing import Any, cast

from ocsf.schema import OcsfSchema, OcsfObject, OcsfEvent, OcsfType
from ocsf.repository import (
    Repository,
    ObjectDefn,
    EventDefn,
    SpecialFiles,
    TypeDefn,
    ExtensionDefn,
    ProfileDefn,
    DictionaryDefn,
    AnyDefinition,
    VersionDefn,
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
                    if not file.data.name.startswith("_"):
                        data = asdict(file.data)
                        _remove_nones(data)

                        schema.objects[file.data.name] = dacite.from_dict(OcsfObject, data)

                elif file.path.startswith(RepoPaths.EVENTS.value):
                    assert file.data is not None
                    assert isinstance(file.data, EventDefn)
                    if file.data.uid is not None and file.data.name != "base_event":
                        assert file.data.name is not None
                        data = asdict(file.data)
                        _remove_nones(data)
                        if file.data.src_extension is not None:
                            name = "/".join([file.data.src_extension, file.data.name])
                        else:
                            name = file.data.name

                        schema.classes[name] = dacite.from_dict(OcsfEvent, data)

                elif file.path == SpecialFiles.DICTIONARY:
                    #types: dict[str, OcsfType] = field(default_factory=dict)
                    assert file.data is not None
                    assert isinstance(file.data, DictionaryDefn)
                    assert file.data.types is not None
                    assert isinstance(file.data.types.attributes, dict)
                    for k, v in file.data.types.attributes.items():
                        if isinstance(v, TypeDefn):
                            data = asdict(v)
                            _remove_nones(data)
                            schema.types[k] = dacite.from_dict(OcsfType, data)

                elif file.path == SpecialFiles.VERSION:
                    assert file.data is not None
                    assert isinstance(file.data, VersionDefn)
                    assert file.data.version is not None
                    schema.version = file.data.version

            except Exception as e:
                raise ValueError(f"Error processing {file.path}: {e}") from e

        # Build type_name, object_name, and object_type.
        # These are really only needed by the OCSF server internals, but we're trying
        # to be as faithful to the server's schema as possible.
        for record in list(schema.classes.values()) + list(schema.objects.values()):
            for attr in record.attributes.values():
                if attr.type in schema.objects:
                    attr.object_name = schema.objects[attr.type].caption
                    attr.object_type = attr.type

                elif attr.type in schema.types:
                    attr.type_name = schema.types[attr.type].caption

                else:
                    raise ValueError(f"Unknown type {attr.type} in {record.name}")

        if "base" in schema.classes:
            schema.base_event = schema.classes["base"]

        return schema
