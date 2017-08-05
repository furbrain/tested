from ..plugins import PluginBase
from collections import namedtuple
import ast
import types
from python2 import ExpressionTypeParser


Entity = namedtuple("Entity", "line name")


def getAliasName(node):
    return node.asname or node.name
    
    
        
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
        
      


