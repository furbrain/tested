from collections import namedtuple
import attr

@attr.s
class Scope():
    name = attr.ib()
    line_start = attr.ib()
    line_end = attr.ib()
    indent = attr.ib()
    context = attr.ib()

    def matches(self, line, indent):
        if self.line_start <= line <= self.line_end:
            if indent >= self.indent:
                return True
        return False

class ScopeList():
    def __init__(self):
        self.scopes = []
    def addScope(self, name, line_start, line_end, indent, context):
        self.scopes.append(Scope(name, line_start, line_end, indent, context))
        
    def getScope(self, line, indent):
        possible_scopes = [x for x in self.scopes if x.matches(line, indent)]
        if possible_scopes:
            return sorted(possible_scopes, key=lambda x: x.indent)[-1]
        return None

