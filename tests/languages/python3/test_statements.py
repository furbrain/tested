import unittest
import ast
from tested.languages.python3 import parse_statements, TypeSet, ClassType

class TestStatementBlockTypeParser__Base(unittest.TestCase):
    def checkStatement(self, stmt, result, field="context", context=None):
        answer = parse_statements(stmt, context)[field]
        message = "%s should return %s: %s, instead returned %s, context is %s" % (stmt, field, result, answer, context)
        self.assertEqual(answer, result)

class TestStatementBlockTypeParser__Assignments(TestStatementBlockTypeParser__Base):        
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
        
    def testMultiLineAssignment(self):
        self.checkStatement("a = 1\nb = 2.0\nc = a+b",{'a':'int','b':'float','c':'float'})
        
    def testAugmentedAssignment(self):
        self.checkStatement("a += 3.0", {'a':'float, int'}, context = {'a':TypeSet(int)})
        
class TestStatementBlockTypeParser__Functions(TestStatementBlockTypeParser__Base):
    def testBasicFunctionDef(self):
        self.checkStatement("def f(): pass", {'f':'f() -> (NoneType)'})

    def testFunctionReturnsNone(self):
        self.checkStatement("def f(): return None", {'f':'f() -> (NoneType)'})

    def testFunctionReturnsInt(self):
        self.checkStatement("def f(): return 1", {'f':'f() -> (int)'})
        
    def testFunctionWithArgs(self):
        self.checkStatement("def f(a, b): pass", {'f':'f(a, b) -> (NoneType)'})

    def testFunctionReturnsOneArg(self):
        self.checkStatement("def f(a): return a", {'f':'f(a) -> (Unknown: a)'})
        
    def testFunctionWithVarargs(self):
        self.checkStatement("def f(a, *b): return b", {'f':'f(a) -> ([Unknown: b])'})
        
    def testFunctonReturnsEitherArg(self):
        func = """
def f(a, b):
    if a:
         return a
    else:
         return b
"""
        self.checkStatement(func, {'f':'f(a, b) -> (Unknown: a, Unknown: b)'})
                
                
class TestStatementBlockTypeParser__Classes(TestStatementBlockTypeParser__Base):
    def testClassCreation(self):
        self.checkStatement("class A(object): pass", {'A':'A'})
        
    def testClassInstanceCreation(self):
        self.checkStatement("class A(object): pass\ninst = A()", {'A':'A','inst':'A<instance>'})
    
    def testClassAttributeCreation(self):
        stmt = "class A(object): pass\nA.b=1"
        results = parse_statements(stmt)
        ctx = results['context']
        self.assertEqual(ctx['A'][0].get_attr('b'),'int')
        
    def testClassVariableCreation(self):
        stmt = "class A(object):\n  b=1"
        results = parse_statements(stmt)
        ctx = results['context']
        self.assertEqual(ctx['A'][0].get_attr('b'),'int')
        
    def testClassVariableDoesNotTransferIntoMethods(self):
        stmt = "class A(object):\n  b=1\n  def test(a):\n    return b"
        results = parse_statements(stmt)
        ctx = results['context']
        self.assertEqual(ctx['A'][0].get_attr('test'),'test(self, a) -> (Unknown:)')
        
        
    def testInstanceMethodCreation(self):
        stmt = "class A(object):\n  def im(self):\n    return self"
        results = parse_statements(stmt)
        ctx = results['context']
        self.assertEqual(ctx['A'][0].get_attr('im'),'im(self) -> (A<instance>)')
        
    def testClassMethodCreation(self):
        stmt = "class A(object):\n  @classmethod\n  def cm(cls):\n    return cls"
        results = parse_statements(stmt)
        ctx = results['context']
        self.assertEqual(ctx['A'][0].get_attr('cm'),'cm(cls) -> (A)')

    def testStaticMethodCreation(self):
        stmt = "class A(object):\n  @staticmethod\n  def sm(a):\n    return a"
        results = parse_statements(stmt)
        ctx = results['context']
        self.assertEqual(ctx['A'][0].get_attr('sm'),'sm(a) -> (Unknown: a)')
    
