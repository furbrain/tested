import ast

from .inferred_types import TypeSet, InferredType, UnknownType

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
    
    def getReturnTypeSet(self, arg_types):
        return_typeset = TypeSet()
        type_mapping = {k:v for k,v in zip(self.args, arg_types)}
        for possible_type in self.returns:
            if isinstance(possible_type,UnknownType):
                return_typeset.add(type_mapping.get(possible_type.type, UnknownType()))
            else:
                return_typeset.add(possible_type)
        return return_typeset
        
    def __str__(self):
        return self.type