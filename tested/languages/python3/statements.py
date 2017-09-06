import ast
from .expressions import get_expression_type
from .inferred_types import TypeSet, UnknownType, InferredList
from .scopes import Scope
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
                    
    def parseStatements(self, nodes):
        for node in nodes:
            self.visit(node)          
        return {'return': self.returns}
                    
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
        from .functions import FunctionType
        self.scope[node.name] =  FunctionType.fromASTNode(node, self.scope)
        
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
        from .classes import ClassType
        print("processing {}".format(node.name))
        self.scope[node.name] = ClassType.fromASTNode(node, self.scope)
        
    def isSequence(self, node):
        return (type(node).__name__ in ("Tuple","List"))
        
    
