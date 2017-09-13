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
        
    def visit_ClassDef(self, node):
        from .classes import ClassType
        self.scope[node.name] = ClassType.fromASTNode(node, self.scope)
        
    def visit_Import(self, node):
        from .modules import ModuleType
        for alias in node.names:
            name = alias.asname or alias.name
            self.scope[name] = ModuleType.fromName(alias.name, self.scope)
            
    def visit_ImportFrom(self, node):
        from .modules import ModuleType
        module = ModuleType.fromName(node.module, self.scope, node.level)
        for alias in node.names:
            name = alias.asname or alias.name
            if not module.has_attr(alias.name):
                if hasattr(module,'outer_scope'):
                    module.set_attr(alias.name, ModuleType.fromName(alias.name, module.outer_scope, level=1))
            self.scope[name] = module.get_attr(alias.name)
        
    def isSequence(self, node):
        return (type(node).__name__ in ("Tuple","List"))
        
    
