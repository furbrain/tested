import ast
import inspect

from .inferred_types import TypeSet, InferredType, UnknownType

def get_parameters(function):
    signature = inspect.signature(function)
    params = signature.parameters
    return params.keys()

class FunctionType(InferredType):

    @classmethod
    def fromASTNode(cls, node, return_type=None):
        name = node.name
        arg_names = [arg.arg for arg in node.args.args]
        docstring = ast.get_docstring(node)
        if return_type is None:
            return_type = UnknownType('return')
        return cls(name, arg_names, return_type, docstring)

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
        self.type = "%s(%s) -> (%s)" % (self.name, ', '.join(args), returns)
        self.docstring = docstring
        
    def __str__(self):
        return self.type
