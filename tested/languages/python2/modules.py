import ast
from statements import StatementTypeParser

class ModuleTypeParser(ast.NodeVisitor):
    def __init__(self, context=None):
        self.context = {}
        if context:
            self.context.update(context)
                      
    def parseModule(self, text):
        syntax_tree = ast.parse(text)
        self.visit(syntax_tree)
        
    def visit_Module(self,node):
        for statement in node.body:
            parser = StatementTypeParser(self.context)
            result = parser.parseStatement(statement)
            self.context.update(result.get('names',{}))
