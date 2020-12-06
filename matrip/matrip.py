import os
from arpeggio.cleanpeg import ParserPEG
from arpeggio import visit_parse_tree
from arpeggio import PTNodeVisitor


aggr_table = [
    "SUM"
]

class Context:

    def __init__(self, tables, group_by):
        self.tables = tables
        self.group_by = group_by


class Measure:

    def __init__(self, aggr, table, field):
        self.table = table
        self.aggr = aggr
        self.field = field

    def name(self):
        return '_'.join([self.aggr, self.table, self.field])

    def expression(self):
        return self.aggr + '(' + self.field + ') AS ' + self.name()


class MatripVisitor(PTNodeVisitor):

    def __init__(self, **kwargs):
        self.measures = []
        self.expressions = []
        super().__init__(kwargs)

    def visit_number(self, node, children):
        if self.debug:
            print("Converting {}.".format(node.value))
        return node.value

    def visit_field(self, node, children):
        if self.debug:
            print("Converting {}.".format(node.value))
        table, field = str(node.value).split(':')
        return table, field

    def visit_aggr(self, node, children):
        if self.debug:
            print("Converting {}.".format(node.value))
        return node.value

    def visit_measure(self, node, children):
        if self.debug:
            print("Measure {}.".format(node.value))

        aggr = children[0]
        table, field = children[1]
        measure = Measure(aggr, table, field)
        self.measures.append(measure)
        return measure.name()

    def visit_factor(self, node, children):
        if self.debug:
            print("Factor {}".format(children))
        if len(children) == 1:
            return children[0]
        return children[0] + children[1]

    def visit_term(self, node, children):
        if self.debug:
            print("Term {}".format(children))
        term = children[0]
        for i in range(2, len(children), 2):
            term += children[i-1] + children[i]
        return term

    def visit_expression(self, node, children):
        if self.debug:
            print("Expression {}".format(children))
        expr = children[0]
        for i in range(2, len(children), 2):
            expr += children[i-1] + children[i]
        self.expressions += [expr]
        return expr


def generate_base_table(measures, expressions, context):
    measures_by_table = {}
    for table in context.tables:
        measures_by_table[table] = [measure for measure in measures if measure.table == table]

    result = ""
    base_by_table = []
    for table in context.tables:
        if len(measures_by_table[table]) == 0:
            continue
        group_by_expression = ','.join(context.group_by)
        values = ','.join([measure.expression() for measure in measures_by_table[table]])
        name = f"{table}_c"
        base_by_table += [name]
        result += f"CREATE MATERIALIZED VIEW {name} AS SELECT {values} FROM {table} GROUP BY {group_by_expression};\n"


    result += f"CREATE VIEW base AS SELECT {','.join(['*'] + expressions)} FROM {base_by_table[0]}"
    for table in base_by_table[1:]:
        on_condtion = []
        for key in context.group_by:
            on_condtion += [f"{table}.{key} = {base_by_table[0]}.{key}"]
        result += f" LEFT JOIN {table} ON {','.join(on_condtion)}"
    result += ";"
    return result


def parse(input_expr, context, debug=False):
    with open(os.path.join(os.path.dirname(__file__), 'matrip.peg'), 'r') as f:
        grammar = f.read()
        parser = ParserPEG(grammar, "matrip", debug=debug)

    parse_tree = parser.parse(input_expr)
    visitor = MatripVisitor(debug=debug)
    visit_parse_tree(parse_tree, visitor)
    return generate_base_table(visitor.measures, visitor.expressions, context)

