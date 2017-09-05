import ast
from .expressions import get_expression_type
from .inferred_types import TypeSet, UnknownType, InferredList
from .functions import FunctionType
from .scopes import Scope
from .classes import ClassType
from .assignment import assign_to_node
from .builtins import get_built_in_for_literal

def parse_statements(statements, scope=None):
    if isinstance(statements,str):
        statements = [ast.parse(statements)]
    parser = StatementBlockTypeParser(scope)
    return parser.parseStatements(statements)

class StatementBlockTypeParser(ast.NodeVisitor):
    def __init__(self, scope):
        self.scope = scope
        self.returns = TypeSet()
        self.scopes = []
                    
    def parseStatements(self, nodes):
        for node in nodes:
            self.visit(node)          
        return {'return': self.returns, 'scopes': self.scopes, 'last_scope': self.scope}
                    
    def visit_Assign(self, node):
        for target in node.targets:
            self.assignToTarget(target,node.value)
            
    def visit_AugAssign(self, node):
        op_node = ast.BinOp(node.target,node.op,node.value)
        self.assignToTarget(node.target,op_node)
        
    def assignToTarget(self, target, value_node):
        if self.isSequence(target) and self.isSequence(value_node):
            for i, subtarget in enumerate(target.elts):
                self.assignToTarget(subtarget, value_node.elts[i])
        else:
            assigned_types = get_expression_type(value_node, self.scope)
            assign_to_node(target, assigned_types, self.scope)

    def visit_FunctionDef(self, node):
        #create function type
        # parse function
        scope = self.get_new_scope_for_function(node)
        results = parse_statements(node.body, scope)
        if results['return']:
            return_val = results['return']
        else:
            return_val = get_built_in_for_literal(None)
        self.scope[node.name] =  FunctionType.fromASTNode(node, return_val)
        self.scopes.append(scope)
        self.scopes.extend(results['scopes'])
        
    def get_new_scope_for_function(self, node):
        scope = Scope(node.name, node.lineno, node.col_offset, parent = self.scope)
        self.set_scope_for_positional_args(node, scope)
        self.set_scope_for_varargs(node, scope)
        function_type = FunctionType.fromASTNode(node)
        scope[node.name] = function_type
        return scope
        
    def set_scope_for_positional_args(self, node, scope):
        args_node = node.args
        for arg in args_node.args:
            name = arg.arg
            scope[name] = UnknownType(name)
        
    def set_scope_for_varargs(self, node, scope):
        args_node = node.args
        if args_node.vararg:
            list_element_type = UnknownType(args_node.vararg.arg)
            inferred_list = InferredList(list_element_type)
            scope[args_node.vararg.arg] = inferred_list
        if args_node.kwarg:
            scope[args_node.kwarg] = InferredDict()


    def visit_ClassDef(self, node):
        scope = Scope(node.name, node.lineno, node.col_offset, self.scope)
        class_type = ClassType.fromASTNode(node,scope)
        results = parse_class_statements(node.body, scope, class_type)
        self.scope[node.name] = ClassType.fromASTNode(node, scope)
        self.scopes.append(scope)
        self.scopes.extend(results['scopes'])
        
    def isSequence(self, node):
        return (type(node).__name__ in ("Tuple","List"))
        
    def visit_Return(self, node):
        if node.value:
            self.returns = self.returns.add_type(get_expression_type(node.value, self.scope))
        else:
            self.returns = self.returns.add_type(get_built_in_for_literal(None))

def parse_class_statements(statements, scope, class_type):
    parser = ClassBlockParser(scope, class_type)
    return parser.parseStatements(statements)    

#this parser modifies function signatures within a class definition        
class ClassBlockParser(StatementBlockTypeParser):
    def __init__(self, scope, class_type):
        self.outer_scope = scope
        super().__init__(scope)
        self.class_type = class_type

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
                
    def node_is_staticmethod(self, node):
        return getattr(node,"id","") == "staticmethod"
            
    def node_is_classmethod(self, node):
        return getattr(node,"id","") == "classmethod"
    
