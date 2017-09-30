import ast
import warnings

from .inferred_types import TypeSet, InferredList, InferredTuple, InferredSet, InferredDict, InferredType, UnknownType, get_type_name
from .builtins import get_built_in_for_literal
from .scopes import Scope

def get_expression_type(expression, scope):
    if scope is None:
        warnings.warn("No scope passed to get_expression_type with expression: {}".format(expression))
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
        
    def getType(self, expression):
        result = self.visit(expression)
        if result is None:
            warnings.warn("Unimplemented code: {}".format(ast.dump(expression)))
            return UnknownType()
        return result
                
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
        items = [self.getType(elt) for elt in node.elts]
        return InferredList(*items)

        
    def visit_Tuple(self, node):
        items = [self.getType(elt) for elt in node.elts]
        return InferredTuple(*items)
        
    def visit_Set(self, node):
        items = [self.getType(elt) for elt in node.elts]
        return InferredSet(*items)

    def visit_Dict(self, node):
        keys = [self.getType(key) for key in node.keys]
        items = [self.getType(value) for value in node.values]
        return InferredDict(keys, items)

    def visit_Call(self, node):
        func_types = self.getType(node.func)
        args = [self.getType(arg_node) for arg_node in node.args]
        return func_types.get_call_return(args)
        
    def visit_Attribute(self, node):
        base_var = self.getType(node.value)
        return base_var.get_attr(node.attr)
                
    def visit_Expr(self, node):
        return self.getType(node.value)
        
    def visit_Module(self, node):
        return self.getType(node.body[0])
            
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
            index = node.slice.value
            index_type = type(node.slice.value).__name__
            if index_type=="Num":
                return value.get_item(index.n)
            else:
                return value.get_item(self.getType(index))
        else:
            if hasattr(value, 'get_slice'):
                return value.get_slice()
            return value
        
    def visit_Compare(self, node):
        return self.bool
        
    def visit_ListComp(self, node):
        scope = self.getScopeForComprehension(node)
        target = get_expression_type(node.elt, scope)
        return InferredList(target)
            
    def visit_SetComp(self, node):
        scope = self.getScopeForComprehension(node)
        target = get_expression_type(node.elt, scope)
        return InferredSet(target)
            
    def visit_DictComp(self, node):
        scope = self.getScopeForComprehension(node)
        key_target = get_expression_type(node.key, scope)
        value_target = get_expression_type(node.value, scope)
        return InferredDict([key_target],[value_target])
        
    def visit_GeneratorExp(self, node):
        scope = self.getScopeForComprehension(node)
        target = get_expression_type(node.elt, scope)
        return InferredIterator(target)
    
    def getScopeForComprehension(self, node):
        from .assignment import assign_to_node
        scope = self.scope
        for generator in node.generators:
            scope = Scope('__listcomp__', node.lineno, node.col_offset, parent=scope)
            iterator = get_expression_type(generator.iter, scope)
            assign_to_node(generator.target, iterator.get_iter(), scope)
        return scope    
