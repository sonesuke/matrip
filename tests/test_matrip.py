from matrip import __version__, parse, Context
import re


def _r(correct):
    correct = re.sub(r"\s+", " ", correct, flags=re.MULTILINE).strip()
    return re.sub(r"\n", " ", correct, flags=re.MULTILINE).strip()


def test_matrip():
    assert __version__ == '0.1.0'


def test_measure_1():
    context = Context(["table_a", "table_b"], ["field_x", "field_y"])
    test = "SUM(table_a:field_a)"
    correct = """
    CREATE MATERIALIZED VIEW table_a_c AS
    SELECT 
        SUM(field_a) AS SUM_table_a_field_a
    FROM 
        table_a
    GROUP BY
        field_x,field_y;
    CREATE VIEW base AS 
    SELECT 
        *
    FROM
        table_a_c;
    """
    assert _r(correct) == _r(parse(test, context))


def test_measure_2():
    context = Context(["table_a", "table_b"], ["field_x", "field_y"])
    test = "SUM(table_a:field_a)+1"
    correct = "abc"
    assert _r(correct) == _r(parse(test, context))


def test_measure_3():
    context = Context(["table_a", "table_b"], ["field_x", "field_y"])
    test = "SUM(table_a:field_a)/COUNT(table_a:field_a)"
    correct = "abc"
    assert _r(correct) == _r(parse(test, context))


def test_measure_4():
    context = Context(["table_a", "table_b"], ["field_x", "field_y"])
    test = "SUM(table_a:field_a)+COUNT(table_b:field_b)"
    correct = "abc"
    assert _r(correct) == _r(parse(test, context))
