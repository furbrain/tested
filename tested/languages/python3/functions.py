import ast
import inspect

from .inferred_types import TypeSet, InferredType, InferredList, InferredDict, UnknownType
from .builtins import get_built_in_for_literal
from .expressions import get_expression_type
from .statements import StatementBlockTypeParser
from .scopes import Scope

def get_parameters(function):
    try:
        signature = inspect.signature(function)
    except ValueError:
        return[]
    params = signature.parameters
    return params.keys()

def node_is_staticmethod(node):
    return getattr(node,"id","") == "staticmethod"
        
def node_is_classmethod(node):
    return getattr(node,"id","") == "classmethod"

def make_arg_dict(node):
    dct = {}
    for arg in node.args:
        name = arg.arg
        dct[name] = UnknownType(name)
    return dct

class FunctionType(InferredType):

    @classmethod
    def fromASTNode(cls, node, parent_scope=None, owning_class=None):
        arg_names = [arg.arg for arg in node.args.args]
        docstring = ast.get_docstring(node)
        self = cls(node.name, arg_names, UnknownType('return'), docstring)
        scope = self.createScopeFromNode(node, parent_scope, owning_class)
        parser = FunctionParser(scope)
        results = parser.parseFunction(node.body)
        if results['return']:
            self.return_values = results['return']
        else:
            self.return_values = get_built_in_for_literal(None)
        return self

    def createScopeFromNode(self, node, parent_scope, owning_class):
        if parent_scope is None:
            parent_scope=Scope('__test__',0,-1)
        scope = Scope(node.name, node.lineno, node.col_offset, parent = parent_scope)
        args_dict = make_arg_dict(node.args)
        if owning_class:
            scope[owning_class.name] = owning_class
            first_arg = node.args.args[0].arg
            if any(node_is_classmethod(n) for n in node.decorator_list):
                args_dict[first_arg] = owning_class
            elif not any(node_is_staticmethod(n) for n in node.decorator_list):
                args_dict[first_arg] = owning_class.instance_type
        for name, arg_type in args_dict.items():
            scope[name] = arg_type
        
        if node.args.vararg:
            list_element_type = UnknownType(node.args.vararg.arg)
            inferred_list = InferredList(list_element_type)
            scope[node.args.vararg.arg] = inferred_list
        if node.args.kwarg:
            scope[node.args.kwarg] = InferredDict()
        scope[node.name] = self
        return scope

    @classmethod
    def fromFunction(cls, function, return_type):
        name = function.__name__
        arg_names = get_parameters(function)
        docstring = function.__doc__
        return cls(name, arg_names, return_type, docstring)
        
    def __init__(self, name, args, returns, docstring):
        super().__init__()
        self.name = name
        self.args = args
        self.return_values = returns
        self.type = "FUNCTION"
        self.docstring = docstring
        
    def __str__(self):
        return "%s(%s) -> (%s)" % (self.name, ', '.join(self.args), self.return_values)
        
class FunctionParser(StatementBlockTypeParser):
    def parseFunction(self, nodes):
        #create function type
        # parse function
        return self.parseStatements(nodes)
            
    def visit_Return(self, node):
        if node.value:
            self.returns = self.returns.add_type(get_expression_type(node.value, self.scope))
        else:
            self.returns = self.returns.add_type(get_built_in_for_literal(None))

