
import os

from ocsf.util import get_schema
from ocsf.compare import compare, ChangedSchema, NoChange
from ocsf.repository import read_repo
from ocsf.compile.compiler import Compilation

def get_diff():
    s1 = get_schema(os.environ["SCHEMA_PATH"])
    s2 = Compilation(read_repo(os.environ["REPO_PATH"])).build()

    return compare(s1, s2)


def test_versus():
    from pprint import pprint
    diff = get_diff()

    assert isinstance(diff, ChangedSchema)

    for name, event in diff.classes.items():
        print(name)
        assert isinstance(event, NoChange)
    pprint(diff.classes)

    #pprint(get_diff())
    assert False
