import unittest
from tested.scopes import indents

class TestLineNumberGetter(unittest.TestCase):
    def checkLineNumbers(self, text, expected):
        result = indents.IndentGetter.get_lines(text)          
        self.assertEqual(result, expected)
        
    def testSimpleAssignment(self):
        self.checkLineNumbers("a = 1",[(1,0)])
        
    def testMultipleAssignment(self):
        self.checkLineNumbers("a = 1\nb = 2",[(1,0),(2,0)])
    
    def testSingleNested(self):
        self.checkLineNumbers("def f(a):\n  return a",[(1,0),(2,2)])
        
    def testNestedFuncs(self):
        self.checkLineNumbers("def f(a,b):\n  def g(b):\n    return a",[(1,0),(2,2),(3,4)])
        
    def testLineNumbersInDocstrings(self):
        self.checkLineNumbers('def f():\n  """\ntest docstring\n"""\n  return f', [(1,0),(5,2)])

