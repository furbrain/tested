import ast

from .expressions import get_expression_type
from .inferred_types import TypeSet, InferredList, InferredType

def isSequence(node):
    return (type(node).__name__ in ("Tuple","List"))

def isStarred(node):
    return type(node).__name__ == "Starred"

def isNode(node):
    return isinstance(node, ast.AST)
    
def isInferredType(node):
    return isinstance(node, (InferredType, TypeSet))
    
def assign_to_node(target, value, scope):
    if isinstance(target, str):
        target = ast.parse(target, mode="eval").body
    if isSequence(target):
        if isNode(value) and isSequence(value):
            for i, subtarget in enumerate(target.elts):
                if isStarred(subtarget):
                    elements = [get_expression_type(x) for x in value.elts[i:]]
                    assign_to_node(subtarget, InferredList(*elements), scope)
                    assign_to_node(subtarget, builtins.create_list(*elements), scope)
                else:
                    assign_to_node(subtarget, value.elts[i], scope)
            return
        elif isInferredType(value):
            for i, subtarget in enumerate(target.elts):
                if isStarred(subtarget):
                    elements = value.get_slice_from(i)
                    assign_to_node(subtarget, elements, scope)
                else:
                    assign_to_node(subtarget, value.get_item(i), scope)
            return
    if isNode(value):
        value = get_expression_type(value, scope)
    parser = Assigner(scope, value)
    parser.visit(target)
    

class Assigner(ast.NodeVisitor):
    def __init__(self, scope, value):
        self.scope = scope
        self.value = value
        
    def visit_Name(self, node):
        name = node.id
        if name in self.scope:
            self.scope[name] = self.scope[name].add_type(self.value)
        else:
            self.scope[name] = self.value
        
    def visit_Attribute(self, node):
        types = get_expression_type(node.value, self.scope)
        attr = node.attr
        types.add_attr(attr, self.value)
                
    def visit_Subscript(self, node):
        types = get_expression_type(node.value, self.scope)
        slice_type = type(node.slice).__name__
        if slice_type=="Index":
            types.add_item(self.value)
        else:
            for val in self.value:
                if isinstance(val, InferredList):
                    types.add_item(val.get_item(0))
            
    def visit_Call(self, node):
        #do nothing as does  not affect scope or classes
        pass
