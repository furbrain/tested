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
            return False
                        
    def __hash__(self):
        return hash(self.name)

class InferredList():
    def __init__(self, *args):
        self.element_types = TypeSet()
        for arg in args:
            self.add(arg)
        
    def add(self, other):
        self.element_types.add(other)
    
    
    def __str__(self):
        return '[%s]' % self.element_types

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
        
    def __repr__(self):
        return "<TypeSet: (%s)>" % self
        
    def __iter__(self):
        return iter(self.types)
        
    def __eq__(self, other):
        if isinstance(other,TypeSet):
            return self.types==other.types
        if isinstance(other,basestring):
            return str(self)==other
        return False
        
class ExpressionTypeParser(ast.NodeVisitor):
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
        
    def visit_Name(self, node):
        if node.id in self.names:
            return self.names[node.id]
            
    def visit_List(self, node):
        result = InferredList()
        for elt in node.elts:
            result.add(self.getType(elt))
        return result
        
    def visit_Expr(self, node):
        return self.visit(node.value)
        
    def visit_Module(self, node):
        return self.visit(node.body[0])
            
    def visit_BinOp(self, node):
        op = type(node.op).__name__
        result = TypeSet()
        for left in self.getType(node.left):
            for right in self.getType(node.right):
                new_type = self.getBinOpType(left, right, op)
                if new_type is not TypeError:
                    result.add(new_type)
        return result
            
    def getBinOpType(self, left, right, op):
        if self.bothArgsNumeric(left,right):
            return self.getHighestPriorityNumber(left, right)
        if self.bothArgsStrings(left, right):
            return self.getHighestPriorityString(left, right)
        if left in STRING_TYPES and right in NUMERIC_TYPES and op=="Mult":
            return left
        if left in STRING_TYPES and op=="Mod":
            return left
        return TypeError
        
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
        
    def visit_Subscript(self, node):
        value = self.getType(node.value)
        slice_type = type(node.slice).__name__
        if slice_type=="Index":
            if isinstance(value,InferredList):
                return value.element_types
        
    def visit_Compare(self, node):
        return TypeSet(bool)
        
class StatementTypeParser(ast.NodeVisitor):
    def __init__(self, names=None):
        self.names = {}
        if names:
            self.names.update(names)
        self.expression_parser = ExpressionTypeParser(self.names)
        
    def parseStatement(self, node):
        return self.visit(node)
            
    def visit_Assign(self, node):
        result = {'names':{}}
        for target in node.targets:
            result['names'].update(self.assignToTarget(target,node.value))
        return result
        
    def assignToTarget(self, target, value_node):
        result = {}
        if self.isSequence(target) and self.isSequence(value_node):
            for i, subtarget in enumerate(target.elts):
                result.update(self.assignToTarget(subtarget, value_node.elts[i]))
        else:
            result[self.visit(target)] = self.expression_parser.getType(value_node)
        return result
        
    def isSequence(self, node):
        return (type(node).__name__ in ("Tuple","List"))
        
    def visit_Return(self, node):
        return {'return':self.expression_parser.getType(node.value)}
        
    def visit_Name(self, node):
        return node.id    
        
    def visit_Expr(self, node):
        return self.visit(node.value)
        
    def visit_Module(self, node):
        return self.visit(node.body[0])
    
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
        
      


