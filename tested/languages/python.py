from ..plugins import PluginBase
from collections import namedtuple
import ast
import inspect
import types


Entity = namedtuple("Entity", "line name")

NUMERIC_TYPES = (int,long,float)
STRING_TYPES = (basestring, unicode, str)

def getAliasName(node):
    return node.asname or node.name
    
class InferredType():
    def __init__(self, tp):
        if inspect.isclass(tp):
            self.type = tp
        else:
            self.type = type(tp)
        self.name = self.type.__name__
        
    def __str__(self):
        return self.name
        
    def __eq__(self, other):
        if isinstance(other,InferredType):
            return self.type == other.type
        elif inspect.isclass(other):
            return self.type == other
        else:
            return self.type == type(other)
            
    def __hash__(self):
        return hash(self.name)

class InferredList():
    def __init__(self):
        self.element_type = TypeSet()
    
    def __str__(self):
        return '[%s]' % self.element_type

class TypeSet():
    def __init__(self, *args):
        self.types = set()
        for a in args:
            self.add(a)

    def add(self, other):
        if isinstance(other,TypeSet):
            self.types.update(other)
        elif isinstance(other,InferredType):
            self.types.add(other)
        else:
            self.types.add(InferredType(other))
            
    def matches(self, type_list):
        return any(x in type_list for x in self.types)        
            
    def __str__(self):
        return ','.join(sorted(str(x) for x in self.types))
        
    def __iter__(self):
        return iter(self.types)
        
class ExpressionTreeVisitor(ast.NodeVisitor):
    def __init__(self, names=None):
        self.names =  {
            'True': TypeSet(bool),
            'False': TypeSet(bool),
            'None': TypeSet(types.NoneType),
        }
        if names is not None:
            self.names.update(names)
        
    def getType(self,expression):
        return self.visit(expression)
        
    def visit_Num(self, node):
        return TypeSet(node.n)
        
    def visit_Str(self, node):
        return TypeSet(node.s)
        
    def visit_Expr(self, node):
        return self.visit(node.value)
        
    def visit_Module(self, node):
        return self.visit(node.body[0])
            
    def visit_BinOp(self, node):
        op = type(node.op).__name__
        result = TypeSet()
        for left in self.getType(node.left):
            for right in self.getType(node.right):
                result.add(self.getBinOpType(left, right, op))
        return result
            
    def getBinOpType(self, left, right, op):
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
        if float in (left,right):
            return float
        elif long in (left,right):
            return long
        else:
            return int
    
    def getHighestPriorityString(self, left, right):
        if unicode in (left,right):
            return unicode
        else:
            return str
    
    def visit_Name(self, node):
        if node.id in self.names:
            return self.names[node.id]
            
    def visit_UnaryOp(self, node):
        op = type(node.op).__name__
        result = TypeSet()
        for operand in self.getType(node.operand):
            if op=="Not":
                result.add(bool)
            if op=="Invert":
                if operand==long:
                    result.add(long)
                else:
                    result.add(int)
            if op in ("UAdd","USub"):
                if operand in NUMERIC_TYPES:
                    result.add(operand)
                else:
                    result.add(int)
        return result
                
    def visit_BoolOp(self, node):
        return TypeSet(bool)
        
    
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
        
      


