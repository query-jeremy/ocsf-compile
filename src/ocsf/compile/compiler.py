from typing import Optional

from ocsf.schema import OcsfSchema
from ocsf.repository import Repository, RepoPath
from .options import CompilationOptions
from .protoschema import ProtoSchema
from .planners.planner import Operation, Planner
from .planners.annotations import AnnotationPlanner
from .planners.set_category import SetCategoryPlanner
from .planners.extension import (
    ExtensionMergePlanner,
    ExtensionCopyPlanner,
    MarkExtensionPlanner,
    ExtensionPrefixPlanner,
)
from .planners.extends import ExtendsPlanner
from .planners.include import IncludePlanner
from .planners.profile import ExcludeProfileAttrsPlanner, MarkProfilePlanner
from .planners.dictionary import DictionaryPlanner
from .planners.uid import UidPlanner
from .planners.object_type import ObjectTypePlanner
from .planners.uid_names import IdSiblingPlanner
from .planners.datetime import DateTimePlanner
from .merge import MergeResult

FileOperations = dict[RepoPath, list[Operation]]
CompilationOperations = list[FileOperations]
CompilationPlan = list[Operation]

FileMutations = list[tuple[Operation, MergeResult]]
CompilationMutations = dict[RepoPath, FileMutations]


class Compilation:
    def __init__(self, repo: Repository, options: CompilationOptions = CompilationOptions()):
        self._operations: Optional[CompilationOperations] = None
        self._plan: Optional[CompilationPlan] = None
        self._mutations: Optional[CompilationMutations] = None
        self._schema: Optional[OcsfSchema] = None
        self._repo = repo
        self._proto = ProtoSchema(repo)

        # [phase: [planner, planner, ...]]
        self._planners: list[list[Planner]] = [
            [
                AnnotationPlanner(self._proto, options),
                MarkExtensionPlanner(self._proto, options),
                MarkProfilePlanner(self._proto, options),
                IncludePlanner(self._proto, options),
                ExtendsPlanner(self._proto, options),
                ExtensionMergePlanner(self._proto, options),
                ExcludeProfileAttrsPlanner(self._proto, options),
            ],
            [SetCategoryPlanner(self._proto, options)],
            [UidPlanner(self._proto, options), DictionaryPlanner(self._proto, options)],
            [
                ExtensionPrefixPlanner(self._proto, options),
                ObjectTypePlanner(self._proto, options),
                IdSiblingPlanner(self._proto, options),
                DateTimePlanner(self._proto, options),
                ExtensionCopyPlanner(self._proto, options),
            ],
        ]

    def analyze(self) -> CompilationOperations:
        operations: CompilationOperations = []
        for phase in self._planners:
            found: FileOperations = {}
            for planner in phase:
                for file in self._repo.files():
                    ops = planner.analyze(file)
                    if ops is not None:
                        if isinstance(ops, Operation):
                            ops = [ops]

                        for op in ops:
                            if op.target not in found:
                                found[op.target] = []
                            found[op.target].append(op)

            operations.append(found)

        self._operations = operations
        return operations

    def order(self, operations: Optional[CompilationOperations] = None) -> CompilationPlan:
        if operations is not None:
            self._operations = operations

        if self._operations is None:
            self.analyze()
            assert self._operations is not None

        plan: CompilationPlan = []

        def follow(path: RepoPath, phase: FileOperations, planned: set[RepoPath]):
            if path in planned or path not in phase:
                return
            planned.add(path)
            for op in phase[path]:
                if op.prerequisite is not None and op.prerequisite not in planned:
                    follow(op.prerequisite, phase, planned)
                plan.append(op)

        for phase in self._operations:
            planned: set[RepoPath] = set()
            for path, _ in phase.items():
                follow(path, phase, planned)

        self._plan = plan
        return plan

    def compile(self, plan: Optional[CompilationPlan] = None) -> CompilationMutations:
        if plan is not None:
            self._plan = plan

        if self._plan is None:
            self.order()
            assert self._plan is not None

        mutations: CompilationMutations = {}
        for op in self._plan:
            if op.target not in mutations:
                mutations[op.target] = []
            result = op.apply(self._proto)
            mutations[op.target].append((op, result))

        self._mutations = mutations
        return mutations

    def build(self) -> OcsfSchema:
        if self._mutations is None:
            self.compile()
            assert self._mutations is not None

        if self._schema is None:
            self._schema = self._proto.schema()

        return self._schema
