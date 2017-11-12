class FunctionParser(statements.StatementBlockTypeParser):
    def parse_function(self, nodes):
        # create function type
        # parse function
        return self.parse_statements(nodes)

    def visit_Return(self, node):
        if node.value:
            self.returns = self.returns.add_type(expressions.get_expression_type(node.value, self.scope))
        else:
            self.returns = self.returns.add_type(builtins.get_built_in_for_literal(None))
            
# this parser modifies function signatures within a class definition
class ClassBlockParser(statements.StatementBlockTypeParser):
    def __init__(self, scope, class_type):
        super().__init__(scope)
        self.class_type = class_type

    def visit_FunctionDef(self, node):
        from .functions import FunctionType
        self.scope[node.name] = FunctionType.from_ast_node(node, self.scope.parent, owning_class=self.class_type)
        
        class ModuleTypeParser(ast.NodeVisitor):

    def parse_module(self, text, module):
        self.scope = scopes.Scope('__main__', line_start=0, indent=-1, line_end=len(text.splitlines()))
        self.scope.module = module
        syntax_tree = ast.parse(text)
        self.visit(syntax_tree)
        return self.scope_list

    def visit_Module(self, node):
        statements.parse_statements(node.body, self.scope)
        lines = LineNumberGetter().process_text(node)
        self.scope_list = self.find_full_scopes(self.scope.get_all_children(), lines, self.scope.line_end)

    def find_full_scopes(self, all_scopes, lines, max_line):
        scope_list = scopes.ScopeList()
        for scope in all_scopes:
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
        if hasattr(node, 'lineno'):
            if node.col_offset >= 0:  # docstrings have col_offset==-1 in cpython: a bug!
                if node.lineno in self.lines:
                    self.lines[node.lineno] = min(node.col_offset, self.lines[node.lineno])
                else:
                    self.lines[node.lineno] = node.col_offset
        super().generic_visit(node)            
