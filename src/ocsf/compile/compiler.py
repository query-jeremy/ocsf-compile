from typing import Optional

from ocsf.schema import OcsfSchema
from ocsf.repository import Repository, RepoPath
from .options import CompilationOptions
from .protoschema import ProtoSchema
from .planners.planner import Operation, Planner
from .planners.extension import ExtensionMergePlanner, ExtensionCopyPlanner
from .planners.extends import ExtendsPlanner
from .planners.include import IncludePlanner
from .planners.dictionary import DictionaryPlanner
from .merge import MergeResult

FileOperations = dict[RepoPath, list[Operation]]
CompilationOperations = list[FileOperations]
CompilationPlan = list[Operation]

FileMutations = list[tuple[Operation, MergeResult]]
CompilationMutations = dict[RepoPath, FileMutations]


class Compilation:
    def __init__(self, repo: Repository, options: CompilationOptions = CompilationOptions()):
        self.operations: Optional[CompilationOperations] = None
        self.plan: Optional[CompilationPlan] = None
        self.mutations: Optional[CompilationMutations] = None
        self.schema: Optional[OcsfSchema] = None
        self._repo = repo
        self._schema = ProtoSchema(repo)

        # [phase: [planner, planner, ...]]
        self._planners: list[list[Planner]] = [
            [
                IncludePlanner(self._schema, options),
                ExtendsPlanner(self._schema, options),
                ExtensionMergePlanner(self._schema, options),
            ],
            [DictionaryPlanner(self._schema, options)],
            [ExtensionCopyPlanner(self._schema, options)],
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

        self.operations = operations
        return operations

    def order(self) -> CompilationPlan:
        if self.operations is None:
            self.analyze()
            assert self.operations is not None

        plan: CompilationPlan = []

        def follow(path: RepoPath, phase: FileOperations, planned: set[RepoPath]):
            if path in planned or path not in phase:
                return
            planned.add(path)
            for op in phase[path]:
                if op.prerequisite is not None and op.prerequisite not in planned:
                    follow(op.prerequisite, phase, planned)
                plan.append(op)

        for phase in self.operations:
            planned: set[RepoPath] = set()
            for path, _ in phase.items():
                follow(path, phase, planned)

        self.plan = plan
        return plan

    def compile(self) -> CompilationMutations:
        if self.plan is None:
            self.order()
            assert self.plan is not None

        mutations: CompilationMutations = {}
        for op in self.plan:
            if op.target not in mutations:
                mutations[op.target] = []
            mutations[op.target].append((op, op.apply(self._schema)))

        self.mutations = mutations
        return mutations

    def build(self) -> OcsfSchema:
        if self.mutations is None:
            self.compile()
            assert self.mutations is not None

        if self.schema is None:
            self.schema = self._schema.schema()

        return self.schema
