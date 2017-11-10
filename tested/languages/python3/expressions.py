import ast
import warnings

from . import inferred_types, builtins, scopes, utils

def get_expression_type(expression, scope):
    if scope is None:
        warnings.warn("No scope passed to get_expression_type with expression: {}".format(expression))
    if isinstance(expression, str):
        expression = ast.parse(expression)
    parser = ExpressionTypeParser(scope)
    return parser.get_type(expression)

class ExpressionTypeParser(ast.NodeVisitor):
    def __init__(self, scope):
        self.scope = scope
        self.float = builtins.get_built_in_for_literal(1.1)
        self.int = builtins.get_built_in_for_literal(1)
        self.str = builtins.get_built_in_for_literal('a')
        self.bool = builtins.get_built_in_for_literal(True)
        self.NUMERIC_TYPES = (self.int, self.float)
        
    def get_type(self, expression):
        result = self.visit(expression)
        if result is None:
            warnings.warn("Unimplemented code: {}".format(ast.dump(expression)))
            return inferred_types.UnknownType()
        return result
                
    def visit_Num(self, node):
        return builtins.get_built_in_for_literal(node.n)
        
    def visit_Str(self, node):
        return builtins.get_built_in_for_literal(node.s)
        
    def visit_Bytes(self, node):
        return builtins.get_built_in_for_literal(node.s)
        
    def visit_Name(self, node):
        if node.id in self.scope:
            return self.scope[node.id]
        else:
            return inferred_types.UnknownType()
    
    def visit_NameConstant(self, node):
        return builtins.get_built_in_for_literal(node.value)
           
    def visit_List(self, node):
        items = self.get_sequence_items(node.elts)
        return builtins.create_list(*items)
        
    def visit_Tuple(self, node):
        items = self.get_sequence_items(node.elts)
        return builtins.create_tuple(*items)
        
    def visit_Set(self, node):
        items = self.get_sequence_items(node.elts)
        return builtins.create_set(*items)

    def get_sequence_items(self, node_list):
        items = []
        for node in node_list:
            if utils.is_ast_starred(node):
                node_type = self.get_type(node.value)
                items.extend(node_type.get_star_expansion())
            else:
                items.append(self.get_type(node))
        return items
        
    def visit_Dict(self, node):
        keys = [self.get_type(key) for key in node.keys]
        items = [self.get_type(value) for value in node.values]
        return builtins.create_dict(keys, items)

    def visit_Call(self, node):
        func_types = self.get_type(node.func)
        args = self.get_sequence_items(node.args)
        return func_types.get_call_return(args)
        
    def visit_Lambda(self, node):
        from .functions import FunctionType
        return FunctionType.from_lambda_node(node, self.scope)    
        
    def visit_Attribute(self, node):
        base_var = self.get_type(node.value)
        return base_var.get_attr(node.attr)
                
    def visit_Expr(self, node):
        return self.get_type(node.value)
        
    def visit_Module(self, node):
        return self.get_type(node.body[0])
        
    def visit_IfExp(self, node):
        return inferred_types.TypeSet(self.get_type(node.body), self.get_type(node.orelse))
            
    def visit_BinOp(self, node):
        op = type(node.op).__name__
        result = inferred_types.TypeSet()
        for left in self.get_type(node.left):
            for right in self.get_type(node.right):
                new_type = self.get_binary_op_type(left, right, op)
                if new_type is not TypeError:
                    result = result.add_type(new_type)
        return result
            
    def get_binary_op_type(self, left, right, op):
        if self.both_args_numeric(left, right):
            return self.get_highest_priority_number(left, right)
        if self.both_args_strings(left, right):
            return self.str
        if left == self.str and right in self.NUMERIC_TYPES and op == "Mult":
            return left
        if left == self.str and op == "Mod":
            return left
        return TypeError
        
    def both_args_numeric(self, left, right):
        return left in self.NUMERIC_TYPES and right in self.NUMERIC_TYPES
            
    def both_args_strings(self, left, right):
        return left == self.str and right == self.str
        
    def get_highest_priority_number(self, left, right):
        if self.float in (left, right):
            return self.float
        else:
            return self.int
    
    def visit_UnaryOp(self, node):
        op = type(node.op).__name__
        if op == "Not":
            return self.bool
        if op == "Invert":
            return self.int
        if op in ("UAdd", "USub"):
            result = inferred_types.TypeSet()
            for operand in self.get_type(node.operand):
                if operand in self.NUMERIC_TYPES:
                    result = result.add_type(operand)
                else:
                    result = result.add_type(self.int)
            return result        
                
    def visit_BoolOp(self, node):
        return self.bool
        
    def visit_Subscript(self, node):
        value = self.get_type(node.value)
        slice_type = type(node.slice).__name__
        if slice_type == "Index":
            index = node.slice.value
            index_type = type(node.slice.value).__name__
            if index_type == "Num":
                return value.get_item(index.n)
            else:
                return value.get_item(self.get_type(index))
        else:
            if hasattr(value, 'get_slice'):
                return value.get_slice()
            return value
        
    def visit_Compare(self, node):
        return self.bool
        
    def visit_ListComp(self, node):
        scope = self.get_scope_for_comprehension(node)
        target = get_expression_type(node.elt, scope)
        return builtins.create_list(target)
            
    def visit_SetComp(self, node):
        scope = self.get_scope_for_comprehension(node)
        target = get_expression_type(node.elt, scope)
        return builtins.create_set(target)
            
    def visit_DictComp(self, node):
        scope = self.get_scope_for_comprehension(node)
        key_target = get_expression_type(node.key, scope)
        value_target = get_expression_type(node.value, scope)
        return builtins.create_dict([key_target], [value_target])
        
    def visit_GeneratorExp(self, node):
        scope = self.get_scope_for_comprehension(node)
        target = get_expression_type(node.elt, scope)
        return inferred_types.InferredIterator(target)
    
    def get_scope_for_comprehension(self, node):
        from .assignment import assign_to_node
        scope = self.scope
        for generator in node.generators:
            scope = scopes.Scope('__listcomp__', node.lineno, node.col_offset, parent=scope)
            iterator = get_expression_type(generator.iter, scope)
            assign_to_node(generator.target, iterator.get_iter(), scope)
        return scope    
