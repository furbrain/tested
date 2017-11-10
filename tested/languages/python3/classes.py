import ast

from . import inferred_types, expressions, statements, scopes

class ClassType(inferred_types.InferredType):
    @classmethod
    def from_ast_node(cls, node, scope=None):
        name = node.name
        parents = [expressions.get_expression_type(x, scope) for x in node.bases]
        docstring = ast.get_docstring(node)
        self = cls(name, parents, docstring)
        self.scope = scopes.Scope(node.name, line_start=node.lineno, indent=node.col_offset, parent=scope)
        parser = ClassBlockParser(self.scope, self)
        parser.parseStatements(node.body)
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


class InstanceType(inferred_types.InferredType):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.name = "<{}>".format(parent)
        self.attrs.update(parent.attrs)

# this parser modifies function signatures within a class definition
class ClassBlockParser(statements.StatementBlockTypeParser):
    def __init__(self, scope, class_type):
        super().__init__(scope)
        self.class_type = class_type

    def visit_FunctionDef(self, node):
        from .functions import FunctionType
        self.scope[node.name] = FunctionType.from_ast_node(node, self.scope.parent, owning_class=self.class_type)
