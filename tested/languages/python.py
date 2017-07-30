from ..plugins import PluginBase
from collections import namedtuple
import ast


Entity = namedtuple("Entity", "line name")

def getAliasName(node):
    return node.asname or node.name

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
        print self.tree_visitor.getEntities(self.parse_tree)
        self.entities = []
        
    def getCandidates(self, line_number, current_characters):
        return []
        
      


