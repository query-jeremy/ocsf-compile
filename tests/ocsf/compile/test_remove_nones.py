

from ocsf.compile.protoschema import _remove_nones

def test_remove_nones():
    d = {
        "a": 1,
        "b": None,
        "c": {
            "d": 2,
            "e": None,
            "f": {
                "g": 3,
                "h": None,
            },
        },
    }
    _remove_nones(d)

    assert "b" not in d
    assert "a" in d
    assert "c" in d
    assert isinstance(d["c"], dict)
    assert "e" not in d["c"]
    assert "d" in d["c"]
    assert "f" in d["c"]
    assert isinstance(d["c"]["f"], dict)
    assert "g" in d["c"]["f"]
    assert "h" not in d["c"]["f"]