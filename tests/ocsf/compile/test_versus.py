import os

from ocsf.util import get_schema
from ocsf.compare import compare, ChangedSchema, NoChange, ChangedEvent
from ocsf.compare.formatter import format
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
    #print(f"--- {os.environ['SCHEMA_PATH']}")
    #print(f"+++ {os.environ['REPO_PATH']}")
    # format(diff)

    # s2 = Compilation(read_repo(os.environ["REPO_PATH"])).build()
    # pprint(s2.objects["device"])

    ok = 0
    bad = 0
    bad_attrs = 0

    for name, event in diff.classes.items():
        fail = 0
        if isinstance(event, ChangedEvent):
            for attr, change in event.attributes.items():
                if not attr.endswith("_dt") and not attr.endswith("_name"):
                    if not isinstance(change, NoChange):
                        print(name, attr, change)
                        fail += 1
            if fail > 0:
                bad += 1
                bad_attrs += fail
        else:
            ok += 1
        # if not isinstance(event, NoChange):
        #    pprint(event)
        # assert isinstance(event, NoChange)
    # pprint(diff.classes)
    print("Good", ok)
    print("Bad", bad)
    print("Bad Attrs", bad_attrs)
    assert bad == 0

    # pprint(get_diff())
    # assert False
