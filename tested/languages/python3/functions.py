import ast

from . import inferred_types, builtins, expressions, statements, scopes, utils

def node_is_staticmethod(node):
    return getattr(node, "id", "") == "staticmethod"

def node_is_classmethod(node):
    return getattr(node, "id", "") == "classmethod"

def make_arg_dict(node):
    dct = {}
    for arg in node.args:
        name = arg.arg
        dct[name] = inferred_types.UnknownType(name)
    return dct

class FunctionType(inferred_types.InferredType):

    @classmethod
    def from_ast_node(cls, node, parent_scope=None, owning_class=None):
        arg_names = [arg.arg for arg in node.args.args]
        docstring = ast.get_docstring(node)
        self = cls(node.name, arg_names, inferred_types.UnknownType('return'), docstring)
        scope = self.create_scope_from_node(node, parent_scope, owning_class)
        parser = FunctionParser(scope)
        results = parser.parse_function(node.body)
        if results['return']:
            self.return_values = results['return']
        else:
            self.return_values = builtins.get_built_in_for_literal(None)
        return self

    @classmethod
    def from_lambda_node(cls, node, scope):
        arg_names = [arg.arg for arg in node.args.args]
        docstring = "Anonymous lambda function"
        self = cls('__lambda__', arg_names, expressions.get_expression_type(node.body, scope), docstring)
        return self

    def create_scope_from_node(self, node, parent_scope, owning_class):
        if parent_scope is None:
            parent_scope = scopes.Scope('__test__', 0, -1)
        scope = scopes.Scope(node.name, node.lineno, node.col_offset, parent=parent_scope)
        args_dict = make_arg_dict(node.args)
        if owning_class:
            scope[owning_class.name] = owning_class
            if node.args.args:  # exclude case where no args applied - likely staticmethod
                first_arg = node.args.args[0].arg
                if any(node_is_classmethod(n) for n in node.decorator_list):
                    args_dict[first_arg] = owning_class
                elif not any(node_is_staticmethod(n) for n in node.decorator_list):
                    args_dict[first_arg] = owning_class.instance_type
        for name, arg_type in args_dict.items():
            scope[name] = arg_type

        if node.args.vararg:
            list_element_type = inferred_types.UnknownType(node.args.vararg.arg)
            inferred_list = builtins.create_list(list_element_type)
            scope[node.args.vararg.arg] = inferred_list
        if node.args.kwarg:
            inferred_dict = builtins.create_dict(keys=[builtins.get_built_in_for_literal('abc')],
                                                 values=[inferred_types.UnknownType()])
            scope[node.args.kwarg.arg] = inferred_dict
        scope[node.name] = self
        return scope

    def __init__(self, name, args, returns, docstring):
        super().__init__()
        self.name = name
        self.args = args
        self.return_values = returns
        self.type = "FUNCTION"
        self.docstring = docstring

    @utils.do_not_recurse('...')
    def __str__(self):
        return "%s(%s) -> (%s)" % (self.name, ', '.join(self.args), self.return_values)

class FunctionParser(statements.StatementBlockTypeParser):
    def parse_function(self, nodes):
        # create function type
        # parse function
        return self.parse_statements(nodes)

    def visit_Return(self, node):
        if node.value:
            self.returns = self.returns.add_type(expressions.get_expression_type(node.value, self.scope))
        else:
            self.returns = self.returns.add_type(builtins.get_built_in_for_literal(None))
