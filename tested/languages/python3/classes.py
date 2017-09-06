from .inferred_types import InferredType, TypeSet
from .expressions import get_expression_type
from .statements import StatementBlockTypeParser
from .scopes import Scope
import ast

class ClassType(InferredType):
    
    @classmethod
    def fromASTNode(cls, node, scope = None):
        name=node.name
        parents = [get_expression_type(x, scope) for x in node.bases]
        docstring = ast.get_docstring(node)
        self = cls(name, parents, scope, docstring)
        self.scope = Scope(node.name, line_start=node.lineno, indent=node.col_offset, parent=scope)
        parser = ClassBlockParser(self.scope, self)
        parser.parseStatements(node.body)
        for k,v in self.scope.context.items():
            self.add_attr(k,v)
        return self
        
    def add_attr(self, attr, typeset):
        super().add_attr(attr, typeset)
        self.instance_type.add_attr(attr, typeset)
        
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

def parse_class_statements(statements, scope, class_type):
    parser = ClassBlockParser(scope, class_type)
    return parser.parseStatements(statements)    

#this parser modifies function signatures within a class definition        
class ClassBlockParser(StatementBlockTypeParser):
    def __init__(self, scope, class_type):
        super().__init__(scope)
        self.class_type = class_type

    def visit_FunctionDef(self, node):
        from .functions import FunctionType
        self.scope[node.name] =  FunctionType.fromASTNode(node, self.scope.parent, owning_class=self.class_type)


    def get_new_scope_for_function(self, node):
        scope = Scope(node.name, node.lineno, node.col_offset, self.scope.parent)
        scope[self.class_type.name] = self.class_type
        self.set_scope_for_positional_args(node, scope)
        self.set_scope_for_varargs(node, scope)
        function_type = FunctionType.fromASTNode(node)
        scope[node.name] = function_type
        return scope    

        
    def set_scope_for_positional_args(self, node, scope):
        args_node = node.args
        if args_node.args:
            name = args_node.args[0].arg
            if any(self.node_is_staticmethod(n) for n in node.decorator_list):
                scope[name] = UnknownType(name)
            elif any(self.node_is_classmethod(n) for n in node.decorator_list):
                scope[name] = self.class_type
            else:
                scope[name] = self.class_type.instance_type
            for arg in args_node.args[1:]:
                name = arg.arg
                scope[name] = UnknownType(name)
                

