from .inferred_types import InferredType
import ast

class ClassType(InferredType):
    
    @classmethod
    def fromASTNode(cls, node, context = None):
        name=node.name
        parents = []
        docstring = ast.get_docstring(node)
        return cls(name, parents, context, docstring)
        
    def __init__(self, name,  parents, context = None, docstring=""):
        super().__init__(None)
        self.name = name
        for parent in parents:
            for tp in parent:
                self.attrs.update(tp.attrs)
        if context:
            self.attrs.update(context)
        self.call_response = lambda x: InstanceType(self)
        
        
class InstanceType(InferredType):
    pass
