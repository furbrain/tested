from .. import itypes, utils

class ModuleRepository:
    known_modules = {}
    @classmethod
    def get_module_from_name(cls, name, scope, level=0):
        parent_module = scope.get_module()
        document = parent_module.document
        filename = module_finder.find_module(name, level, parent_module.filename, document.location)
        return cls.get_module_from_filename(filename, name, scope)
    
    @classmethod    
    def get_module_from_file_name(cls, filename, name, scope):
        if filename in cls.known_modules:
            return cls.known_modules[filename]
        parent_module = scope.get_module()
        mod = itypes.ModuleType(name, parent_module.document, filename)
        try:
            with open(filename) as f:
                mod = module_from_text(f.read(), filename, parent_module.document)
                cls.known_modules[filename] = mod
        except (IOError, TypeError):
            mod = inferred_types.UnknownType()
            cls.known_modules[filename] = mod
        return mod

def module_from_text(text, filename, document):
    mod = itypes.ModuleType(name, document, filename)
    scope = scopes.Scope('__main__', line_start=0, indent=-1, line_end=len(text.splitlines()))
    scope.module = mod
    mod_node = utils.get_matching_node(text, 'Module')
    statements.parse_statements(mod_node.body, scope)
    lines = LineNumberGetter().process_text(node)
    mod.scope_list = scope.create_scope_list(lines)
    mod.scope = scope
    for name, typeset in scope.context.items():
        mod.add_attr(name, typeset)
    return mod    
    
