from collections import namedtuple

Scope = namedtuple("Scope", 'line_start line_end indent context')

def scopeMatches(scope, line, indent):
    if scope.line_start <= line <= scope.line_end:
        if indent >= scope.indent:
            return True
    return False

class ScopeList():
    def __init__(self):
        self.scopes = []
    def addScope(self, line_start, line_end, indent, context):
        self.scopes.append(Scope(line_start, line_end, indent, context))
        
    def getScope(self, line, indent):
        possible_scopes = [x for x in self.scopes if scopeMatches(x, line, indent)]
        if possible_scopes:
            return sorted(possible_scopes, key=lambda x: x.indent)[-1]
        return None

