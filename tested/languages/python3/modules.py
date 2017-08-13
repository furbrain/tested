import ast
from .statements import StatementBlockTypeParser

class ModuleTypeParser(ast.NodeVisitor):
    def __init__(self):
        self.context = {}

    def parseModule(self, text):
        syntax_tree = ast.parse(text)
        self.visit(syntax_tree)
        
    def visit_Module(self,node):
        parser = StatementBlockTypeParser(self.context)
        results = parser.parseStatements(node.body)
        self.context.update(results['context'])
