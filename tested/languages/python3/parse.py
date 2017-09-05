import ast
from . import modules, expressions

def parse_text(text):
    parser = modules.ModuleTypeParser()
    return parser.parseModule(text)
    
def get_suggestions(context, line, line_number):
    indent = len(line) - len(line.lstrip(' '))
    scope = context.getScope(line_number, indent)
    identifier = get_last_whole_identifier(line)
    obj,_,prefix = identifier.rpartition('.')
    if obj=='' and prefix=='':
        return []
    if obj:
        scope = expressions.get_expression_type(obj,scope).get_all_attrs()
    return [x for x in scope if x.startswith(prefix)]
    
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

