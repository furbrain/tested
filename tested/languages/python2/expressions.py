import ast
import types

from inferred_types import TypeSet, InferredList

NUMERIC_TYPES = (int,long,float)
STRING_TYPES = (basestring, unicode, str)


class ExpressionTypeParser(ast.NodeVisitor):
    def __init__(self, names=None):
        self.names =  {
            'True': TypeSet(bool),
            'False': TypeSet(bool),
            'None': TypeSet(types.NoneType),
        }
        if names is not None:
            self.names.update(names)
        
    def getType(self,expression):
        return self.visit(expression)
        
    def visit_Num(self, node):
        return TypeSet(node.n)
        
    def visit_Str(self, node):
        return TypeSet(node.s)
        
    def visit_Name(self, node):
        if node.id in self.names:
            return self.names[node.id]
            
    def visit_List(self, node):
        result = InferredList()
        for elt in node.elts:
            result.add(self.getType(elt))
        return result
        
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
                    result.add(new_type)
        return result
            
    def getBinOpType(self, left, right, op):
        if self.bothArgsNumeric(left,right):
            return self.getHighestPriorityNumber(left, right)
        if self.bothArgsStrings(left, right):
            return self.getHighestPriorityString(left, right)
        if left in STRING_TYPES and right in NUMERIC_TYPES and op=="Mult":
            return left
        if left in STRING_TYPES and op=="Mod":
            return left
        return TypeError
        
    def bothArgsNumeric(self,left,right):
        return left in NUMERIC_TYPES and right in NUMERIC_TYPES
            
    def bothArgsStrings(self, left, right):
        return left in STRING_TYPES and right in STRING_TYPES
        
    def getHighestPriorityNumber(self, left, right):
        if float in (left,right):
            return float
        elif long in (left,right):
            return long
        else:
            return int
    
    def getHighestPriorityString(self, left, right):
        if unicode in (left,right):
            return unicode
        else:
            return str
    
    def visit_UnaryOp(self, node):
        op = type(node.op).__name__
        result = TypeSet()
        for operand in self.getType(node.operand):
            if op=="Not":
                result.add(bool)
            if op=="Invert":
                if operand==long:
                    result.add(long)
                else:
                    result.add(int)
            if op in ("UAdd","USub"):
                if operand in NUMERIC_TYPES:
                    result.add(operand)
                else:
                    result.add(int)
        return result
                
    def visit_BoolOp(self, node):
        return TypeSet(bool)
        
    def visit_Subscript(self, node):
        value = self.getType(node.value)
        slice_type = type(node.slice).__name__
        if slice_type=="Index":
            if isinstance(value,InferredList):
                return value.element_types
        
    def visit_Compare(self, node):
        return TypeSet(bool)
