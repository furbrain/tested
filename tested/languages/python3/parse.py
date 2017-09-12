import ast
from . import document, expressions

def parse_text(text, location):
    return document.Document(text, location)
    
def get_suggestions(document, line, line_number):
    indent = len(line) - len(line.lstrip(' '))
    scope = document.scopes.getScope(line_number, indent)
    last_char = line[-1]
    if last_char.isidentifier() or last_char=='.':
        identifier = get_last_whole_identifier(line)
        obj,_,prefix = identifier.rpartition('.')
        if obj=='' and prefix=='':
            return []
        if obj:
            try:
                obj = expressions.get_expression_type(obj,scope)
                scope = obj.get_all_attrs()
                print(scope)
            except SyntaxError:
                pass
        return [x for x in scope if x.startswith(prefix)]
    else:
        return []
        

def get_last_whole_identifier(line):
    if line=='':
        return ''
    if line.endswith('.'):
       return get_last_whole_identifier(line[:-1])+'.'
    if not (line[-1].isidentifier() or line[-1] in (']','}',')')):
        return ''
    for i in range(len(line)):
        try:
            result = ast.parse(line[i:], mode='eval')
        except SyntaxError:
            continue
        else:
            line = line[i:]
            body = result.body
            expr_type = type(body).__name__
            if expr_type=="BinOp":
                return get_line_part(line, body.right)
            elif expr_type=="UnaryOp":
                return get_line_part(line, body.operand)
            elif expr_type=="Compare":
                return get_line_part(line, body.comparators[-1]) 
            elif expr_type=="Tuple":
                return get_line_part(line, body.elts[-1])
            return line
    return ""
    
def get_line_part(line, node):
    line = line[node.col_offset:]
    return get_last_whole_identifier(line)
    
#do ifexp

