import ast

from inferred_types import TypeSet, InferredType, UnknownType

class FunctionType(InferredType):

    @classmethod
    def fromASTNode(cls, node, return_type=None):
        name = node.name
        arg_names = [arg.id for arg in node.args.args]
        docstring = ast.get_docstring(node)
        if return_type is None:
            return_type = TypeSet(UnknownType('return'))
        return cls(name, arg_names, return_type, docstring)
        
    def __init__(self, name, args, returns, docstring):
        self.name = name
        self.args = args
        self.returns = returns
        self.type = "f(%s) -> (%s)" % (', '.join(args), returns)
        self.docstring = docstring
    
    
        
    def __str__(self):
        return self.type
