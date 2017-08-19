import ast
from .statements import parse_statements

class ModuleTypeParser(ast.NodeVisitor):
    def __init__(self):
        self.context = {}

    def parseModule(self, text):
        syntax_tree = ast.parse(text)
        self.visit(syntax_tree)
        
    def visit_Module(self,node):
        results = parse_statements(node.body, self.context)
        self.context.update(results['context'])
