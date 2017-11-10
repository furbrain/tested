import ast
import sys

from . import inferred_types, statements, scopes, module_finder

# set document path to specific locale...
class set_path():
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.old_path = sys.path
        sys.path = self.path + [x for x in sys.path if 'gedit' not in x.lower()]

    def __exit__(self, exc_type, exc_value, traceback):
        sys.path = self.old_path

class ModuleType(inferred_types.InferredType):
    known_modules = {}

    @classmethod
    def from_name(cls, name, scope, level=0):
        parent_module = scope.get_module()
        document = parent_module.document
        filename = module_finder.find_module(name, level, parent_module.filename, document.location)
        if filename in cls.known_modules:
            return cls.known_modules[filename]
        self = cls()
        self.name = name
        parent_module = scope.get_module()
        self.document = parent_module.document
        self.filename = filename
        cls.known_modules[filename] = self
        try:
            with open(self.filename) as f:
                self.parse_text(f.read())
        except (IOError, TypeError):
            self = inferred_types.UnknownType()
            cls.known_modules[filename] = self
        return self

    @classmethod
    def from_text(cls, text, filename, document):
        self = cls()
        self.name = '__main__'
        self.filename = filename
        self.document = document
        self.parse_text(text)
        return self

    def parse_text(self, text):
        parser = ModuleTypeParser()
        self.scope_list = parser.parse_module(text, self)
        self.outer_scope = parser.scope
        for name, typeset in self.outer_scope.context.items():
            self.add_attr(name, typeset)

    def get_outer_scope(self):
        return self.outer_scope

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
