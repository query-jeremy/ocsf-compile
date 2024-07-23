from ocsf.schema import to_json
from ocsf.repository import read_repo

from .compiler import Compilation


PATH = "/Users/jfisher/Source/ocsf/ocsf-schema"

repo = read_repo(PATH, preserve_raw_data=True)
compiler = Compilation(repo)

TARGET = "events/discovery/job_query.json"
from pprint import pprint

analysis = compiler.analyze()
order = compiler.order()
compile = compiler.compile()
schema = compiler.build()

print("ORDER")
prereqs: set[str] = set()
def find_op(target: str):
    for o in order:
        if o.target == target:
            if o.prerequisite is not None:
                find_op(o.prerequisite)
                prereqs.add(o.prerequisite)
            #pprint(o)
    return None
find_op(TARGET)

print()
print("COMPILE")
    
for prereq in prereqs:
    if prereq in compile:
        pprint(compile[prereq])
pprint(compile[TARGET])
