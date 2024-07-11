from ocsf.repository import read_repo

from .compiler import Compilation


PATH = "/Users/jfisher/Source/ocsf/ocsf-schema"

repo = read_repo(PATH, preserve_raw_data=True)
compiler = Compilation(repo)


from pprint import pprint

analysis = compiler.analyze()
order = compiler.order()
compile = compiler.compile()

print("ANALYSIS PHASE 0")
pprint(analysis[0]["objects/databucket.json"])

print("ANALYSIS PHASE 1")
pprint(analysis[1]["objects/databucket.json"])

print("ORDER")
for o in order:
    if o.target == "objects/databucket.json":
        pprint(o)

print("COMPILE")
pprint(compile["objects/databucket.json"])
# pprint(compiler._schema["objects/databucket.json"])
pprint(compiler.build())
