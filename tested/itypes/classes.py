import ast

from . import basics

class ClassType(basics.InferredType):
    @classmethod
    def from_ast_node(cls, node, scope=None):
        name = node.name
        parents = [expressions.get_expression_type(x, scope) for x in node.bases]
        docstring = ast.get_docstring(node)
        self = cls(name, parents, docstring)
        self.scope = scopes.Scope(node.name, line_start=node.lineno, indent=node.col_offset, parent=scope)
        parser = ClassBlockParser(self.scope, self)
        parser.parse_statements(node.body)
        for k, v in self.scope.context.items():
            self.add_attr(k, v)
        return self

    def add_attr(self, attr, typeset):
        super().add_attr(attr, typeset)
        self.instance_type.add_attr(attr, typeset)

    def __init__(self, name,  parents, docstring=""):
        super().__init__()
        self.name = name
        for parent in parents:
            for tp in parent:
                self.attrs.update(tp.attrs)
        self.instance_type = InstanceType(self)
        self.return_values = self.instance_type
        
    def get_call_return(self, arg_list):
        return self.instance_type


class InstanceType(basics.InferredType):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.name = "<{}>".format(parent)
        self.attrs.update(parent.attrs)
