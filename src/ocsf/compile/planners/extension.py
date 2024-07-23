from copy import deepcopy
from dataclasses import dataclass

from ..protoschema import ProtoSchema
from ..options import CompilationOptions
from ..merge import merge, MergeResult
from .planner import Operation, Planner, Analysis
from ocsf.repository import DefinitionFile, extension, extensionless, ObjectDefn, EventDefn, as_path, RepoPaths, SpecialFiles, ExtensionDefn


@dataclass(eq=True, frozen=True)
class ExtensionModifyOp(Operation):
    def apply(self, schema: ProtoSchema) -> MergeResult:
        assert self.prerequisite is not None

        effected = schema[self.target]
        assert effected.data is not None

        source = schema[self.prerequisite]
        assert source.data is not None

        return merge(effected.data, source.data)

    def __str__(self):
        return f"Extension modifies {self.target} <- {self.prerequisite}"


class ExtensionMergePlanner(Planner):
    def __init__(self, schema: ProtoSchema, options: CompilationOptions):
        if options.extensions is None:
            options.extensions = list(schema.repo.extensions())

        if options.ignore_extensions is not None:
            options.extensions = [ext for ext in options.extensions if ext not in options.ignore_extensions]

        super().__init__(schema, options)

    def analyze(self, input: DefinitionFile) -> Analysis:
        # We forcibly initialize this in __init__; this assertion is for the
        # type checker's benefit.
        assert self._options.extensions is not None

        extn = extension(input.path)

        if extn is not None and extn in self._options.extensions:
            dest = extensionless(input.path)
            if dest in self._schema.repo:
                return ExtensionModifyOp(dest, input.path)

        return None


@dataclass(eq=True, frozen=True)
class ExtensionCopyOp(Operation):
    def apply(self, schema: ProtoSchema) -> MergeResult:
        assert self.prerequisite is not None

        source = schema[self.prerequisite]
        assert source.data is not None

        if not isinstance(source.data, ObjectDefn) and not isinstance(source.data, EventDefn):
            return []

        # Look up the source extension name from extension.json (because it may not match the directory)
        extn_dir = extension(self.prerequisite)
        assert extn_dir is not None
        extn = schema[as_path(RepoPaths.EXTENSIONS, extn_dir, SpecialFiles.EXTENSION)]
        assert isinstance(extn.data, ExtensionDefn)
        assert extn.data.name is not None
        source.data.src_extension = extn.data.name

        schema[self.target] = deepcopy(source)
        dest = schema[self.target]
        assert dest.data is not None

        # Here we merge just so that we have a MergeResult. This is slightly
        # inefficient but effective.
        return merge(dest.data, source.data, overwrite=True)

    def __str__(self):
        return f"Extension creates {self.target} <- {self.prerequisite}"


class ExtensionCopyPlanner(ExtensionMergePlanner):
    def analyze(self, input: DefinitionFile) -> Analysis:
        # We forcibly initialize this in __init__; this assertion is for the
        # type checker's benefit.
        assert self._options.extensions is not None

        extn = extension(input.path)

        if extn is not None and extn in self._options.extensions:
            dest = extensionless(input.path)
            if dest not in self._schema.repo:
                return ExtensionCopyOp(dest, input.path)

        return None
