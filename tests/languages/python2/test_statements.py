import unittest
import ast
from tested.languages.python2 import StatementTypeParser

class TestStatementTypeParser(unittest.TestCase):
    def checkStatement(self, stmt, result, field="names", names=None):
        answer = self.parseStatement(stmt, names)[field]
        message = "%s should return %s: %s, instead returned %s, context is %s" % (stmt, field, result, answer, names)
        self.assertEqual(answer, result)

    def parseStatement(self, stmt, names=None):
        syntax_tree = ast.parse(stmt)
        parser = StatementTypeParser(names)
        return parser.parseStatement(syntax_tree)
        
    def testSimpleAssignment(self):
        self.checkStatement("a=1", {'a':"int"})
        self.checkStatement("a=1+2.0", {'a':"float"})
        self.checkStatement("a='abc %d' % 1", {'a':"str"})
        
    def testMultipleAssignment(self):
        self.checkStatement("a,b = 2,3", {'a':'int','b':'int'})
        self.checkStatement("[a,b] = [2,'abc']", {'a':'int','b':'str'})
    
    def testNestedAssignment(self):
        self.checkStatement("(a,b),c = (1,2),3", {'a':'int','b':'int','c':'int'})
        
    def testMultipleTargetAssignment(self):
        self.checkStatement("a = b = 2", {'a':'int','b':'int'})
        
    def testReturnValue(self):
        self.checkStatement("return 'abc'",'str',field="return")
        self.checkStatement("return 2",'int',field="return")
        
