"""Development-only extension of frozen v2 to a moved Click formatting block.

This is target-informed. Scope/AST checks are applicability filters, not a
semantic safety proof. Ambiguity and unsupported shapes preserve input bytes.
"""
import ast
import copy
from template_skill import apply as strict_apply

SCOPES = ('get_help_record', 'get_help_extra')

def dump(node):
    return ast.dump(node, include_attributes=False)

def binding_names(tree):
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            names.add(node.id)
        elif isinstance(node, ast.arg):
            names.add(node.arg)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.alias):
            names.add(node.asname or node.name.split('.')[0])
    return names

def compare_name(test):
    if (isinstance(test, ast.Compare) and isinstance(test.left, ast.Name)
        and len(test.ops) == len(test.comparators) == 1
        and isinstance(test.ops[0], ast.Eq)
        and isinstance(test.comparators[0], ast.Constant)
        and test.comparators[0].value == ''):
        return test.left.id
    return None

def assignment(stmt, value):
    return (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1
            and isinstance(stmt.targets[0], ast.Name) and dump(stmt.value) == dump(value))

def match_branch(node, function):
    if not isinstance(node, ast.If):
        return None
    test, guarded = node.test, False
    variable = compare_name(test)
    if variable is None and isinstance(test, ast.BoolOp) and isinstance(test.op, ast.And) and len(test.values) == 2:
        variable = compare_name(test.values[1])
        if variable and dump(test.values[0]) == dump(ast.parse('isinstance(' + variable + ', str)', mode='eval').body):
            guarded = True
        else:
            return None
    if variable is None or len(node.body) != 1 or len(node.orelse) != 1:
        return None
    if not assignment(node.body[0], ast.Constant(value='""')):
        return None
    if not assignment(node.orelse[0], ast.parse('str(' + variable + ')', mode='eval').body):
        return None
    output = node.body[0].targets[0].id
    if node.orelse[0].targets[0].id != output or not function.args.args:
        return None
    receiver = function.args.args[0].arg
    assignments = [n for n in ast.walk(function) if isinstance(n, ast.Assign)
                   and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
                   and n.targets[0].id == variable]
    if len(assignments) != 1:
        return None
    value = assignments[0].value
    if not (isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute)
            and isinstance(value.func.value, ast.Name) and value.func.value.id == receiver
            and value.func.attr == 'get_default' and len(value.args) == 1
            and len(value.keywords) == 1 and value.keywords[0].arg == 'call'
            and isinstance(value.keywords[0].value, ast.Constant) and value.keywords[0].value.value is False):
        return None
    return {'node': node, 'variable': variable, 'output': output,
            'scope': 'Option.' + function.name, 'guarded': guarded}

def apply(source, frozen_v2):
    def abstain(reason):
        return source, {'decision': reason, 'changed': False}
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return abstain('ABSTAIN_SYNTAX_ERROR')
    if {'str', 'isinstance'} & binding_names(tree):
        return abstain('ABSTAIN_SHADOWED_BUILTIN')
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Option']
    if len(classes) != 1:
        return abstain('ABSTAIN_SCOPE_MISMATCH')
    functions = [n for n in classes[0].body if isinstance(n, ast.FunctionDef) and n.name in SCOPES]
    if len({n.name for n in functions}) != len(functions):
        return abstain('ABSTAIN_AMBIGUOUS_MATCH')
    matches = []
    for function in functions:
        # Do not match an inner function, lambda, or comprehension.
        stack = list(function.body)
        while stack:
            node = stack.pop()
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
                continue
            match = match_branch(node, function)
            if match:
                matches.append(match)
            stack.extend(ast.iter_child_nodes(node))
    try:
        strict_output = strict_apply(source, frozen_v2)
    except ValueError as exc:
        if str(exc) not in ('Precondition mismatch; do not apply', 'Scope must identify exactly one function'):
            raise
        strict_output = None
    if strict_output is not None:
        if matches:
            return abstain('ABSTAIN_AMBIGUOUS_MATCH')
        return strict_output, {'decision': 'APPLIED_FROZEN_V2', 'changed': True,
                               'scope': frozen_v2['scope'], 'guard_source': 'GUARDED_TEMPLATE_V2.json'}
    if len(matches) > 1:
        return abstain('ABSTAIN_AMBIGUOUS_MATCH')
    if not matches:
        return abstain('ABSTAIN_PRECONDITION_MISMATCH')
    match = matches[0]
    if match['guarded']:
        return abstain('ABSTAIN_ALREADY_GUARDED')
    # Take the condition from frozen v2, not from target_after.
    template = ast.parse(frozen_v2['after_function'])
    guards = [n.test for n in ast.walk(template) if isinstance(n, ast.If)
              and dump(n.test) == dump(ast.parse("isinstance(default_value, str) and default_value == ''", mode='eval').body)]
    if len(guards) != 1:
        raise ValueError('Frozen v2 guard is not unique')
    guard = copy.deepcopy(guards[0])
    for node in ast.walk(guard):
        if isinstance(node, ast.Name) and node.id == 'default_value':
            node.id = match['variable']
    test = match['node'].test
    lines = source.encode('utf-8').splitlines(keepends=True)
    start = sum(map(len, lines[:test.lineno - 1])) + test.col_offset
    end = sum(map(len, lines[:test.end_lineno - 1])) + test.end_col_offset
    raw = source.encode('utf-8')
    original = raw[start:end]
    replacement = ('isinstance(' + match['variable'] + ', str) and ').encode() + original
    result = (raw[:start] + replacement + raw[end:]).decode('utf-8')
    expected = copy.deepcopy(tree)
    target = next(n for n in ast.walk(expected) if isinstance(n, ast.If)
                  and n.test.lineno == test.lineno and n.test.col_offset == test.col_offset)
    target.test = guard
    assert dump(ast.parse(result)) == dump(expected)
    return result, {'decision': 'APPLIED_ANCHORED_V2_GUARD', 'changed': True,
                    'scope': match['scope'], 'input_variable': match['variable'],
                    'output_variable': match['output'], 'start_byte': start, 'end_byte': end,
                    'guard_source': 'GUARDED_TEMPLATE_V2.json', 'outside_edit_bytes_preserved': True}
