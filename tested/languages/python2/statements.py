import ast
from expressions import ExpressionTypeParser
from inferred_types import TypeSet

class StatementBlockTypeParser(ast.NodeVisitor):
    def __init__(self, names=None):
        self.names = {}
        self.returns = TypeSet()
        if names:
            self.names.update(names)
            
    def getExpressionType(self, node):
        expression_parser = ExpressionTypeParser(self.names)
        return expression_parser.getType(node)
        
    def parseStatements(self, nodes):
        for node in nodes:
            self.visit(node)          
        return {'names':self.names, 'return': self.returns}
                    
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
            self.names[self.visit(target)] = self.getExpressionType(value_node)
        
    def isSequence(self, node):
        return (type(node).__name__ in ("Tuple","List"))
        
    def visit_Return(self, node):
        self.returns.add(self.getExpressionType(node.value))
        
    def visit_Name(self, node):
        return node.id
