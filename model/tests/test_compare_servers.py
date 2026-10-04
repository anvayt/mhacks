"""Pure compatibility comparison tests; no server calls."""
from model.scripts.compare_servers import compare_numeric, endpoint_params, parse_numbers


def compare(a, b):
    return compare_numeric(parse_numbers(a), parse_numbers(b))


def test_additive_fields_are_allowed():
    assert compare('{"a":1,"b":[2.0,3],"text":"old"}', '{"a":1,"b":[2.0,3,9],"text":"new","extra":7}') == []


def test_numeric_spelling_and_missing_fields_fail():
    diffs = compare('{"a":1,"b":[2.0,3],"c":0.001}', '{"a":1.0,"b":[2.0],"c":1e-3}')
    assert [d["path"] for d in diffs] == ["/a", "/b/1", "/c"]
    assert diffs[1]["reason"] == "missing_numeric_leaf"


def test_strings_booleans_and_null_cannot_replace_a_number():
    for value in ['"1"', 'true', 'null', '{}', '[]']:
        assert compare('{"a":1}', '{"a":'+value+'}')[0]["reason"] == "numeric_type_changed"
    assert compare('{"a":true,"b":null}', '{}') == []  # only numeric leaves are this check's contract


def test_container_type_and_nested_paths_are_checked():
    assert compare('{"a":[{"value":4}]}', '{"a":{"0":{"value":4}}}')[0]["reason"] == "missing_numeric_leaf"
    assert compare('{"a/b~":{"c":2}}', '{"a/b~":{}}')[0]["path"] == "/a~1b~0/c"


def test_bill_request_has_no_opt_in_or_unsupported_parameters():
    source = {"lat":42.2,"lon":-83.7,"unit_sqft":1000,"building_type":"house","block_group":"123"}
    assert endpoint_params("bill_check",source) == {"lat":42.2,"lon":-83.7,"unit_sqft":1000,
                                                   "year":2026,"month":2,"gas_ccf":100}
    assert endpoint_params("weather",source) == {"lat":42.2,"lon":-83.7,"mode":"normal"}
    assert endpoint_params("estimate",source) == source | {"mode":"normal"}
