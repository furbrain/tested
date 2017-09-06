import ast
from .statements import parse_statements
from .scopes import Scope, ScopeList

class ModuleTypeParser(ast.NodeVisitor):

    def parseModule(self, text):
        self.text = text
        syntax_tree = ast.parse(self.text)
        self.visit(syntax_tree)
        return self.scope_list
        
    def visit_Module(self,node):
        self.scope = Scope('__main__', line_start = 0, indent = -1,line_end =len(self.text.splitlines()))
        results = parse_statements(node.body, self.scope)
        lines = LineNumberGetter().process_text(node)
        self.scope_list = self.find_full_scopes(self.scope.get_all_children(), lines, self.scope.line_end)
        
    def find_full_scopes(self, scopes, lines, max_line):
        scope_list = ScopeList()
        for scope in scopes:
            indent = scope.indent
            line_start = scope.line_start
            possible_finish_lines = [line for line in lines if line[0]>line_start and line[1]<=indent]
            if possible_finish_lines:
                scope.line_end = min(possible_finish_lines)[0]
            else:
                scope.line_end = max_line
            scope_list.add(scope)
        return scope_list
        
class LineNumberGetter(ast.NodeVisitor):
    @classmethod
    def get_lines(cls, text):
        parser = cls()
        node = ast.parse(text)
        return parser.process_text(node)
    
    def process_text(self, node):
        self.lines = {}
        self.visit(node)
        return sorted(list(self.lines.items()))
        
    def generic_visit(self, node):
        if hasattr(node,'lineno'):
            if node.lineno in self.lines:
                self.lines[node.lineno] = min(node.col_offset,self.lines[node.lineno])
            else:
                self.lines[node.lineno] = node.col_offset
        super().generic_visit(node) 
           
            
