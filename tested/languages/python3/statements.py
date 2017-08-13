import ast
from .expressions import ExpressionTypeParser
from .inferred_types import TypeSet, UnknownType, InferredList
from .functions import FunctionType
from .scopes import Scope

class StatementBlockTypeParser(ast.NodeVisitor):
    def __init__(self, context=None):
        self.context = {}
        self.returns = TypeSet()
        self.scopes = []
        if context:
            self.context.update(context)
            
    def getExpressionType(self, node):
        expression_parser = ExpressionTypeParser(self.context)
        return expression_parser.getType(node)
        
    def parseStatements(self, nodes):
        for node in nodes:
            self.visit(node)          
        return {'context':self.context, 'return': self.returns, 'scopes': self.scopes}
                    
    def visit_Assign(self, node):
        for target in node.targets:
            self.assignToTarget(target,node.value)
            
    def visit_AugAssign(self, node):
        op_node = ast.BinOp(node.target,node.op,node.value)
        self.assignToTarget(node.target,op_node)
        
    def visit_FunctionDef(self, node):
        #create function type
        # parse function
        ctx = self.context.copy()
        for arg in node.args.args:
            name = arg.id
            ctx[name] = TypeSet(UnknownType(name))
        if node.args.vararg:
            list_element_type = UnknownType(node.args.vararg)
            inferred_list = InferredList(list_element_type)
            ctx[node.args.vararg] = TypeSet(inferred_list)
        if node.args.kwarg:
            ctx[node.args.kwarg] = TypeSet(InferredDict())
        function_type = FunctionType.fromASTNode(node)
        ctx[node.name] = TypeSet(function_type)
        block_parser = StatementBlockTypeParser(ctx)
        results = block_parser.parseStatements(node.body)
        if results['return']:
            return_val = results['return']
        else:
            return_val = TypeSet(None)
        self.context[node.name] = TypeSet(FunctionType.fromASTNode(node, return_val))
        self.scopes.append(Scope(node.lineno,-1,node.col_offset,results['context']))
        self.scopes.append(results['scopes'])

    def assignToTarget(self, target, value_node):
        if self.isSequence(target) and self.isSequence(value_node):
            for i, subtarget in enumerate(target.elts):
                self.assignToTarget(subtarget, value_node.elts[i])
        else:
            self.context[self.visit(target)] = self.getExpressionType(value_node)
        
    def isSequence(self, node):
        return (type(node).__name__ in ("Tuple","List"))
        
    def visit_Return(self, node):
        self.returns.add(self.getExpressionType(node.value))
        
    def visit_Name(self, node):
        return node.id
