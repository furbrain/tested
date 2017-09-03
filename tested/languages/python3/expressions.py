import ast
import types

from .inferred_types import TypeSet, InferredList, InferredType, UnknownType, get_type_name
from .builtins import get_built_in_for_literal


def get_expression_type(expression, scope):
    if isinstance(expression,str):
        expression = ast.parse(expression)
    parser = ExpressionTypeParser(scope)
    return parser.getType(expression)

class ExpressionTypeParser(ast.NodeVisitor):
    def __init__(self, scope):
        self.scope = scope
        self.float = get_built_in_for_literal(1.1)
        self.int = get_built_in_for_literal(1)
        self.str = get_built_in_for_literal('a')
        self.bool = get_built_in_for_literal(True)
        self.NUMERIC_TYPES = (self.int, self.float)
        
    def getType(self,expression):
        return self.visit(expression)
        
    def visit_Num(self, node):
        return get_built_in_for_literal(node.n)
        
    def visit_Str(self, node):
        return get_built_in_for_literal(node.s)
        
    def visit_Name(self, node):
        if node.id in self.scope:
            return self.scope[node.id]
        else:
            return UnknownType()
    
    def visit_NameConstant(self, node):
        return get_built_in_for_literal(node.value)
           
    def visit_List(self, node):
        result = InferredList()
        for elt in node.elts:
            result.add_item(self.getType(elt))
        return result
        
    def visit_Call(self, node):
        func_types = self.visit(node.func)
        args = [self.visit(arg_node) for arg_node in node.args]
        return func_types.get_call_return(args)
        
    def visit_Attribute(self, node):
        result = TypeSet()
        var_types = self.visit(node.value)
        return var_types.get_attr(node.attr)
                
    def visit_Expr(self, node):
        return self.visit(node.value)
        
    def visit_Module(self, node):
        return self.visit(node.body[0])
            
    def visit_BinOp(self, node):
        op = type(node.op).__name__
        result = TypeSet()
        for left in self.getType(node.left):
            for right in self.getType(node.right):
                new_type = self.getBinOpType(left, right, op)
                if new_type is not TypeError:
                    result = result.add_type(new_type)
        return result
            
    def getBinOpType(self, left, right, op):
        if self.bothArgsNumeric(left,right):
            return self.getHighestPriorityNumber(left, right)
        if self.bothArgsStrings(left, right):
            return self.str
        if left == self.str and right in self.NUMERIC_TYPES and op=="Mult":
            return left
        if left == self.str and op=="Mod":
            return left
        return TypeError
        
    def bothArgsNumeric(self,left,right):
        return left in self.NUMERIC_TYPES and right in self.NUMERIC_TYPES
            
    def bothArgsStrings(self, left, right):
        return left == self.str and right == self.str
        
    def getHighestPriorityNumber(self, left, right):
        if self.float in (left,right):
            return self.float
        else:
            return self.int
    
    def visit_UnaryOp(self, node):
        op = type(node.op).__name__
        if op=="Not":
            return self.bool
        if op=="Invert":
            return self.int
        if op in ("UAdd","USub"):
            result = TypeSet()
            for operand in self.getType(node.operand):
                if operand in self.NUMERIC_TYPES:
                    result = result.add_type(operand)
                else:
                    result = result.add_type(self.int)
            return result        
                
    def visit_BoolOp(self, node):
        return self.bool
        
    def visit_Subscript(self, node):
        value = self.getType(node.value)
        slice_type = type(node.slice).__name__
        if slice_type=="Index":
            return value.get_item(0)
        else:
            return value
        
    def visit_Compare(self, node):
        return self.bool

