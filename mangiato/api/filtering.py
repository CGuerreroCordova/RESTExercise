"""
Define logic of parsing queries string for filtering. Provide function to
parse and convert a query filter
"""

import pyparsing as pp

COMPLEX_EXPR = pp.Forward()
OPERATOR = pp.Regex("ge|le|ne|gt|lt|eq").setName("operator")
LOGICAL = (pp.Keyword("and") | pp.Keyword("or")).setName("logical")
DATES = pp.Word(pp.nums + "-" + ":")
NAME = pp.Word(pp.alphas, pp.alphanums + "_" + " ")
QUOTED = pp.Suppress("'") + NAME + pp.Suppress("'") ^ \
         pp.Suppress('"') + NAME + pp.Suppress('"') ^ \
         pp.Suppress('"') + DATES + pp.Suppress('"') ^ \
         pp.Suppress("'") + DATES + pp.Suppress("'")
FIELD = pp.Word(pp.alphas, pp.alphanums + "_")
VALUES = pp.Regex(r"[+-]?\d+(:?\.\d*)?(:?[eE][+-]?\d+)?") | \
         pp.Word(pp.alphas, pp.alphanums + "_") | QUOTED | DATES
CONDITION = (FIELD + OPERATOR + VALUES)
CLAUSE = pp.Group(CONDITION ^ (pp.Suppress("(") +
                               COMPLEX_EXPR + pp.Suppress(")")))
EXPR = pp.operatorPrecedence(CLAUSE, [("and", 2, pp.opAssoc.RIGHT,),
                                      ("or", 2, pp.opAssoc.RIGHT,), ])
COMPLEX_EXPR <<= EXPR
REPLACEMENTS = {"eq": "==", "ne": "!=", "gt": ">", "lt": "<", "ge": ">=",
                "le": "<="}


def process_query(model, string_query):
    """
    Process a query string to detect operators and conditions and convert to
    an sql query with operators of sqlalchemy library. First convert to lower
    all alpha characters, divide query into nested listed having account
    precedence operators suppressing parenthesis, after that process list to
    convert to sqlalchemy query apply multiple recursion on list.
    :param model: Model name which query come from.
    :type: str
    :param string_query: query to parse
    :type: str
    :return: sqlalchemy query parsed
    """
    string_query = string_query.lower()
    parsed = COMPLEX_EXPR.parseString(string_query, parseAll=True)
    query = _process_list_conditions(model, parsed)
    return query


def _process_list_conditions(model, parsed_list):
    """
    Giving a parsed query in nested list apply recursion on it, converting to
    string base case of recursion.
    Base case: Condition without logic operators on it.
    Recursive case: List with logic operators.
    :param model: Model name which query come from.
    :type: str
    :param parsed_list:
    :type: List of list of list of ...
    :return: sqlalchemy query parsed
    """
    processing = parsed_list
    while len(processing) == 1:
        processing = processing[0]
    if processing[1] not in {'and', 'or'}:
        return _process_condition(model, processing)
    return processing[1] + "_(" + \
           _process_list_conditions(model, processing[0]) + ", " + \
           _process_list_conditions(model, processing[2]) + ")"


def _template_condition(model, field_model, operator_condition, value):
    """
    Convert to sqlalchemy query string input parameters.
    :param model: Model to include in the query
    :type: str
    :param field_model: field of model to make comparison
    :type: str
    :param operator_condition: Operator of comparison
    :type: str
    :param value: value of comparison
    :type: str
    :return: Sqlalchemy query in string format
    """
    value = _add_quotes(field_model, value)
    template = "{model}.{field_model} {op} {valor}"
    operator_condition = _replace_operator(operator_condition)
    return template.format(model=model, field_model=field_model,
                           op=operator_condition, valor=value)


def _process_condition(model, comparison):
    """
    Convert to string query sqlalchemy an irreducible list of list. Divide
    elements of list to call function to convert to string query
    :param model: Model to include in the query
    :type: str
    :param comparison: irreducible list
    :type: list[str]
    :return: result of calling function to create sqlalchemy query
    :type: str
    """
    return _template_condition(model, comparison[0], comparison[1],
                               comparison[2])


def _replace_operator(query_api):
    """
    Perform replacement operators from 'eq' 'lt' 'ge' to '==' '<' '>', etc
    :param query_api: Operator in string format acceptable by Mangiato API
    :type: str
    :return: Operator converted to sqlalchemy syntax
    :type: str
    """
    for i, j in REPLACEMENTS.items():
        query_api = query_api.replace(i, j)
    return query_api


def _add_quotes(field_condition, value_condition):
    """
    Add quotes to value if field belongs to group of fields of type date, time,
     str. That fields are enumerated
    :param field_condition: Field of condition
    :type: str
    :param value_condition: value of condition
    :type: str
    :return: value quoted (if it necessary)
    """
    new_value = value_condition
    fields_str_date_time = {'username', 'first_name', 'last_name', 'date',
                            'confirmed_on', 'name', 'description', 'time',
                            'description', 'email', 'status'}
    if field_condition in fields_str_date_time:
        new_value = "'" + value_condition + "'"
    return new_value
