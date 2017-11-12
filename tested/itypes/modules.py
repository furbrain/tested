import ast
import sys

from . import basics

# set document path to specific locale...
class set_path():
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.old_path = sys.path
        sys.path = self.path + [x for x in sys.path if 'gedit' not in x.lower()]

    def __exit__(self, exc_type, exc_value, traceback):
        sys.path = self.old_path

class ModuleType(basics.InferredType):
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


