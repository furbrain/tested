from collections import namedtuple
import attr

@attr.s
class Scope():
    name = attr.ib()
    line_start = attr.ib()
    indent = attr.ib()
    parent = attr.ib(default=None)
    line_end = attr.ib(default=-1)
    context = attr.ib(default=attr.Factory(dict))

    def __getitem__(self, key):
        if key in self.context:
            return self.context[key]
        if self.parent:
            return self.parent[key]
        raise KeyError("Scope Key: {} not found".format(key))
        
    def __contains__(self, key):
        try:
            self.__getitem__(key)
            return True
        except KeyError:
            return False    
        
    def __setitem__(self, key, value):
        self.context[key] = value
        
    def __iter__(self):
        return iter(self.context)

    def matches(self, line, indent):
        if self.line_start <= line <= self.line_end:
            if indent > self.indent:
                return True
        return False
        
    def get_whole_context(self):
        new_ctx = self.context.copy()
        if self.parent:
            new_ctx.update(self.parent.get_whole_context())
        return new_ctx

class ScopeList():
    def __init__(self):
        self.scopes = []
        
    def add(self, scope):
        self.scopes.append(scope)
                
    def getScope(self, line, indent):
        possible_scopes = [x for x in self.scopes if x.matches(line, indent)]
        if possible_scopes:
            return sorted(possible_scopes, key=lambda x: x.indent)[-1]
        return None
        
    def __iter__(self):
        return iter(self.scopes)

