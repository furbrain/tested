import ast
import inspect

from .inferred_types import TypeSet, InferredType, InferredList, UnknownType
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

class FunctionType(InferredType):

    @classmethod
    def fromASTNode(cls, node, scope=None, owning_class=None):
        if scope is None:
            scope=Scope('__test__',0,-1)
        name = node.name
        arg_names = [arg.arg for arg in node.args.args]
        docstring = ast.get_docstring(node)
        self = cls(name, arg_names, UnknownType('return'), docstring)
        self.scope = Scope(node.name, node.lineno, node.col_offset, parent = scope)
        args_node = node.args
        if owning_class is None:
            for arg in args_node.args:
                name = arg.arg
                self.scope[name] = UnknownType(name)
        else:            
            self.scope[owning_class.name] = owning_class
            name = args_node.args[0].arg
            if any(self.node_is_staticmethod(n) for n in node.decorator_list):
                self.scope[name] = UnknownType(name)
            elif any(self.node_is_classmethod(n) for n in node.decorator_list):
                self.scope[name] = owning_class
            else:
                self.scope[name] = owning_class.instance_type
            for arg in args_node.args[1:]:
                name = arg.arg
                self.scope[name] = UnknownType(name)
        if args_node.vararg:
            list_element_type = UnknownType(args_node.vararg.arg)
            inferred_list = InferredList(list_element_type)
            self.scope[args_node.vararg.arg] = inferred_list
        if args_node.kwarg:
            self.scope[args_node.kwarg] = InferredDict()
        self.scope[node.name] = self
        parser = FunctionParser(self.scope)
        results = parser.parseFunction(node.body)
        if results['return']:
            self.return_values = results['return']
        else:
            self.return_values = get_built_in_for_literal(None)
        return self

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

    def node_is_staticmethod(self, node):
        return getattr(node,"id","") == "staticmethod"
            
    def node_is_classmethod(self, node):
        return getattr(node,"id","") == "classmethod"
        
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

