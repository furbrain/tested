from ..plugins import PluginBase
from collections import namedtuple
import ast


Entity = namedtuple("Entity", "line name")

NUMERIC_TYPES = ('int', 'long', 'float')
STRING_TYPES = ('basestring', 'unicode', 'str')

def getAliasName(node):
    return node.asname or node.name
    
class ExpressionTreeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.builtin_constants =  {
            'True': 'bool',
            'False': 'bool',
            'None': 'NoneType',
        }
        
    def getType(self,expression):
        return self.visit(expression)
        
    def visit_Num(self, node):
        return type(node.n).__name__
        
    def visit_Str(self, node):
        return type(node.s).__name__
        
    def visit_Expr(self, node):
        return self.visit(node.value)
        
    def visit_Module(self, node):
        return self.visit(node.body[0])
            
    def visit_BinOp(self, node):
        left = self.getType(node.left)
        right = self.getType(node.right)
        op = type(node.op).__name__
        if self.bothArgsNumeric(left,right):
            return self.getHighestPriorityNumber(left, right)
        if self.bothArgsStrings(left, right):
            return self.getHighestPriorityString(left, right)
        if left in STRING_TYPES and right in NUMERIC_TYPES and op=="Mult":
            return left
        
    def bothArgsNumeric(self,left,right):
        return left in NUMERIC_TYPES and right in NUMERIC_TYPES
            
    def bothArgsStrings(self, left, right):
        return left in STRING_TYPES and right in STRING_TYPES
        
    def getHighestPriorityNumber(self, left, right):
        if 'float' in (left,right):
            return 'float'
        elif 'long' in (left,right):
            return 'long'
        else:
            return 'int'
    
    def getHighestPriorityString(self, left, right):
        if 'unicode' in (left,right):
            return 'unicode'
        else:
            return 'str'
    
    def visit_Name(self, node):
        if node.id in self.builtin_constants:
            return self.builtin_constants[node.id]
            
    def visit_UnaryOp(self, node):
        op = type(node.op).__name__
        operand = self.getType(node.operand)
        if op=="Not":
            return "bool"
        if op=="Invert":
            if operand=="long":
                return "long"
            else:
                return "int"
        if op in ("UAdd","USub"):
            if operand in NUMERIC_TYPES:
                return operand
            else:
                return "int"
                
    def visit_BoolOp(self, node):
        return "bool" 
        
    
class SyntaxTreeVisitor(ast.NodeVisitor):
    def visit_Import(self,node):
        for f in node.names:
            self.appendEntity(node.lineno,getAliasName(f))
        self.generic_visit(node)
        
    def appendEntity(self,line,name):
            self.entities.append(Entity(line=line, name=name))

    def visit_ImportFrom(self,node):
        self.visit_Import(node)
        
    def visit_Assign(self,node):
        self.extractEntities(node.targets)
                
    def extractEntities(self,nodes):
        for f in nodes:
            if isinstance(f,ast.Name):
                self.appendEntity(f.lineno,f.id)
            if isinstance(f,ast.Tuple):
                self.extractEntities(f.elts)
 ###FIXME - need to include attribute and index accesses here...   
 
    def visit_FunctionDef(self,node):
        self.appendEntity(node.lineno,node.name)
        for i in node.args.args:
            self.appendEntity(node.lineno,i.id)
        if node.args.vararg:
            self.appendEntity(node.lineno,node.args.vararg)
        if node.args.kwarg:
            self.appendEntity(node.lineno,node.args.kwarg)
        self.generic_visit(node)        
        
    def getEntities(self,node):
        self.entities= []
        self.visit(node)
        return self.entities

class PythonPlugin(PluginBase):
    def parseText(self, text):
        """Parse a python source file, generate a list of identifiers (classes, functions, variables)
           and possible completions for each of these"""
        self.parse_tree = ast.parse(text)
        self.tree_visitor = SyntaxTreeVisitor()
        self.entities = []
        
    def getCandidates(self, line_number, current_characters):
        return []
        
      


