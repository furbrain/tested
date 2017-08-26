import ast

from .expressions import get_expression_type
from .inferred_types import TypeSet, InferredList

def assign_to_node(node, value, context):
    if isinstance(node,str):
        node = ast.parse(node)
    parser = Assigner(context, value)
    parser.visit(node)

class Assigner(ast.NodeVisitor):
    def __init__(self, context, value):
        self.context = context
        self.value = value
        
    def visit_Name(self, node):
        name = node.id
        if name in self.context:
            self.context[name] = self.context[name].add_type(self.value)
        else:
            self.context[name] = self.value
        
    def visit_Attribute(self, node):
        types = get_expression_type(node.value, self.context)
        attr = node.attr
        types.add_attr(attr, self.value)
                
    def visit_Subscript(self, node):
        types = get_expression_type(node.value, self.context)
        slice_type = type(node.slice).__name__
        if slice_type=="Index":
            types.add_item(self.value)
        else:
            for val in self.value:
                if isinstance(val, InferredList):
                    types.add_item(val.get_item(0))
            
    def visit_Call(self, node):
        #do nothing as does  not affect context or classes
        pass
