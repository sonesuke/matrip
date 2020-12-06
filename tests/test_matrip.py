from matrip import __version__, parse, Context
import re


def _r(correct):
    correct = re.sub(r"\s+", " ", correct, flags=re.MULTILINE).strip()
    correct = re.sub(r",\s+", ",", correct, flags=re.MULTILINE).strip()
    return re.sub(r"\n", " ", correct, flags=re.MULTILINE).strip()


def test_matrip():
    assert __version__ == '0.1.0'


def test_measure_1():
    context = Context(["table_a", "table_b"], ["field_x", "field_y"])
    test = "SUM(table_a:field_a);"
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
        SUM_table_a_field_a
    FROM
        table_a_c;
    """
    assert _r(correct) == _r(parse(test, context))


def test_measure_2():
    context = Context(["table_a", "table_b"], ["field_x", "field_y"])
    test = "SUM(table_a:field_a)+1;"
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
        SUM_table_a_field_a+1
    FROM
        table_a_c;
    """
    assert _r(correct) == _r(parse(test, context))


def test_measure_3():
    context = Context(["table_a", "table_b"], ["field_x", "field_y"])
    test = "SUM(table_a:field_a)/COUNT(table_a:field_a);"
    correct = """
    CREATE MATERIALIZED VIEW table_a_c AS
    SELECT
        SUM(field_a) AS SUM_table_a_field_a,
        COUNT(field_a) AS COUNT_table_a_field_a
    FROM
        table_a
    GROUP BY
        field_x,field_y;
    CREATE VIEW base AS
    SELECT
        SUM_table_a_field_a/COUNT_table_a_field_a
    FROM
        table_a_c;
    """
    print(_r(correct))
    assert _r(correct) == _r(parse(test, context))


def test_measure_4():
    context = Context(["table_a", "table_b"], ["field_x", "field_y"])
    test = "SUM(table_a:field_a)+COUNT(table_b:field_b);"
    correct = """
    CREATE MATERIALIZED VIEW table_a_c AS
    SELECT
        SUM(field_a) AS SUM_table_a_field_a
    FROM
        table_a
    GROUP BY
        field_x,field_y;
    CREATE MATERIALIZED VIEW table_b_c AS
    SELECT
        COUNT(field_b) AS COUNT_table_b_field_b
    FROM
        table_b
    GROUP BY
        field_x,field_y;
    CREATE VIEW base AS
    SELECT
        SUM_table_a_field_a+COUNT_table_b_field_b
    FROM
        table_a_c
        LEFT JOIN table_b_c ON table_b_c.field_x = table_a_c.field_x,table_b_c.field_y = table_a_c.field_y;
    """
    assert _r(correct) == _r(parse(test, context))


def test_measure_5():
    context = Context(["table_a", "table_b"], ["field_x", "field_y"])
    test = "(SUM(table_a:field_a)+COUNT(table_b:field_b))*2;"
    correct = """
    CREATE MATERIALIZED VIEW table_a_c AS
    SELECT
        SUM(field_a) AS SUM_table_a_field_a
    FROM
        table_a
    GROUP BY
        field_x,field_y;
    CREATE MATERIALIZED VIEW table_b_c AS
    SELECT
        COUNT(field_b) AS COUNT_table_b_field_b
    FROM
        table_b
    GROUP BY
        field_x,field_y;
    CREATE VIEW base AS
    SELECT
        (SUM_table_a_field_a+COUNT_table_b_field_b)*2
    FROM
        table_a_c
        LEFT JOIN table_b_c ON table_b_c.field_x = table_a_c.field_x,table_b_c.field_y = table_a_c.field_y;
    """
    assert _r(correct) == _r(parse(test, context))


def test_measure_6():
    context = Context(["table_a", "table_b"], ["field_x", "field_y"])
    test = "SUM(table_a:field_a);COUNT(table_a:field_a);"
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
        SUM_table_a_field_a
    FROM
        table_a_c;
    """
    assert _r(correct) == _r(parse(test, context))
