from .inferred_types import InferredType, TypeSet
import ast

class ClassType(InferredType):
    
    @classmethod
    def fromASTNode(cls, node, context = None):
        name=node.name
        parents = []
        docstring = ast.get_docstring(node)
        return cls(name, parents, context, docstring)
        
    def __init__(self, name,  parents, scope = None, docstring=""):
        super().__init__()
        self.name = name
        for parent in parents:
            for tp in parent:
                self.attrs.update(tp.attrs)
        if scope:
            self.attrs.update(scope.context)
        self.instance_type = InstanceType(self)
        self.return_values= self.instance_type
        
        
class InstanceType(InferredType):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.name = "<{}>".format(parent)
        self.attrs.update(parent.attrs)

