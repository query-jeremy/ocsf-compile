from dataclasses import dataclass
from pathlib import PurePath

from ..protoschema import ProtoSchema
from ..options import CompilationOptions
from ..merge import MergeResult
from .planner import Operation, Planner, Analysis
from ocsf.repository import DefinitionFile, ProfileDefn, ObjectDefn, EventDefn, as_path, extension, RepoPaths, AttrDefn


@dataclass(eq=True, frozen=True)
class ExcludeProfileOp(Operation):
    def apply(self, schema: ProtoSchema) -> MergeResult:
        result: MergeResult = []

        assert self.prerequisite is not None

        target = schema[self.target]
        assert target.data is not None
        assert isinstance(target.data, ObjectDefn) or isinstance(target.data, EventDefn)

        if target.data.attributes is None:
            return result

        profile = schema[self.prerequisite]
        assert profile.data is not None
        assert isinstance(profile.data, ProfileDefn)

        if profile.data.attributes is not None:
            for attr in profile.data.attributes:
                if attr in target.data.attributes:
                    result.append(("attributes", attr))
                    del target.data.attributes[attr]

        return result

    def __str__(self):
        return f"Exclude Profile {self.target} <- {self.prerequisite}"


@dataclass(eq=True, frozen=True)
class MarkProfileOp(Operation):

    def apply(self, schema: ProtoSchema) -> MergeResult:
        result: MergeResult = []

        assert self.prerequisite is not None

        target = schema[self.target]
        assert target.data is not None
        assert isinstance(target.data, ObjectDefn) or isinstance(target.data, EventDefn)

        if target.data.attributes is None:
            return result

        profile = schema[self.prerequisite]
        profile_name = PurePath(self.prerequisite).stem
        assert profile.data is not None
        assert isinstance(profile.data, ProfileDefn)

        if profile.data.attributes is not None:
            for attr in profile.data.attributes:
                if attr in target.data.attributes:
                    defn = target.data.attributes[attr]
                    if isinstance(defn, AttrDefn):
                        result.append(("attributes", attr, "profile"))
                        defn.profile = profile_name


        return result

    def __str__(self):
        return f"Mark Profile {self.target} <- {self.prerequisite}"


def _find_profile(schema: ProtoSchema, profile_ref: str, relative_to: str) -> str | None:
    # extn/profile_name
    # profiles/profile_name.json
    # <extn>/profiles/profile_name.json

    profile_name = PurePath(profile_ref).stem
    search = [profile_ref, as_path(RepoPaths.PROFILES, profile_name + ".json")]

    extn = extension(relative_to)
    if extn is not None:
        search.append(as_path(RepoPaths.EXTENSIONS, extn, RepoPaths.PROFILES, profile_name + ".json"))

    for path in reversed(search):
        if path in schema.repo:
            return path

    return None


class ProfilePlanner(Planner):
    def __init__(self, schema: ProtoSchema, options: CompilationOptions):
        if options.profiles is None:
            options.profiles = list(schema.repo.profiles())

        if options.ignore_profiles is not None:
            options.profiles = [prof for prof in options.profiles if prof not in options.ignore_profiles]

        super().__init__(schema, options)

    def analyze(self, input: DefinitionFile) -> Analysis:
        assert self._options.profiles is not None

        if isinstance(input.data, ObjectDefn) or isinstance(input.data, EventDefn):
            if input.data.profiles is not None:
                # profile_ref will be in one of the following formats:
                #   extension/profile_name
                #   profiles/profile_name
                #   profiles/profile_name.json
                for profile_ref in input.data.profiles:
                    path = _find_profile(self._schema, profile_ref, input.path)
                    if PurePath(profile_ref).stem in self._options.profiles and path is not None:
                        return MarkProfileOp(input.path, path)
                    else:
                        return ExcludeProfileOp(input.path, path)

        return None
