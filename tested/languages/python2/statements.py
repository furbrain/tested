import ast
from expressions import ExpressionTypeParser

class StatementTypeParser(ast.NodeVisitor):
    def __init__(self, names=None):
        self.names = {}
        if names:
            self.names.update(names)
        self.expression_parser = ExpressionTypeParser(self.names)
        
    def parseStatement(self, node):
        return self.visit(node)
            
    def visit_Assign(self, node):
        result = {'names':{}}
        for target in node.targets:
            result['names'].update(self.assignToTarget(target,node.value))
        return result
        
    def assignToTarget(self, target, value_node):
        result = {}
        if self.isSequence(target) and self.isSequence(value_node):
            for i, subtarget in enumerate(target.elts):
                result.update(self.assignToTarget(subtarget, value_node.elts[i]))
        else:
            result[self.visit(target)] = self.expression_parser.getType(value_node)
        return result
        
    def isSequence(self, node):
        return (type(node).__name__ in ("Tuple","List"))
        
    def visit_Return(self, node):
        return {'return':self.expression_parser.getType(node.value)}
        
    def visit_Name(self, node):
        return node.id    
        
    def visit_Expr(self, node):
        return self.visit(node.value)
        
    def visit_Module(self, node):
        return self.visit(node.body[0])

