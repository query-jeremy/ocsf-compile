from ocsf.schema import to_json
from ocsf.repository import read_repo

from .compiler import Compilation


PATH = "/Users/jfisher/Source/ocsf/ocsf-schema"

repo = read_repo(PATH, preserve_raw_data=True)
compiler = Compilation(repo)

TARGET = "objects/device.json"
from pprint import pprint

analysis = compiler.analyze()
order = compiler.order()
compile = compiler.compile()

print("ANALYSIS PHASE 0")
try:
    pprint(analysis[0][TARGET])
except KeyError:
    pass

print("ANALYSIS PHASE 1")
try:
    pprint(analysis[1][TARGET])
except KeyError:
    pass

print("ORDER")
try:
    for o in order:
        if o.target == TARGET:
            pprint(o)
except KeyError:
    pass

print("COMPILE")
try:
    pprint(compile[TARGET])
except KeyError:
    pass
# pprint(compiler.build())
