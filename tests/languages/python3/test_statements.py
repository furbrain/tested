import unittest
import ast
from tested.languages.python3 import parse_statements, TypeSet, ClassType, Scope

class TestStatementBlockTypeParser__Base(unittest.TestCase):
    def checkStatement(self, stmt, result, field="context", context=None):
        if field=="context":
            answer = self.getContext(stmt, context)
        else:
            scope = self.make_Scope(context)
            answer = parse_statements(stmt, scope)[field]
        message = "%s should return %s: %s, instead returned %s, context is %s" % (stmt, field, result, answer, context)
        self.assertEqual(answer, result)

    def getContext(self, stmt, context = None):
        scope = self.make_Scope(context)
        return parse_statements(stmt, scope)['last_scope'].get_whole_context()     
        
    def make_Scope(self, context = None):
        if context:
            return Scope('',0,0,context=context)
        else:
            return Scope('',0,0)
                

class TestStatementBlockTypeParser__Assignments(TestStatementBlockTypeParser__Base):        
    def testSimpleAssignment(self):
        self.checkStatement("a=1", {'a':"<int>"})
        self.checkStatement("a=1+2.0", {'a':"<float>"})
        self.checkStatement("a='abc %d' % 1", {'a':"<str>"})
        
    def testMultipleAssignment(self):
        self.checkStatement("a,b = 2,3", {'a':'<int>','b':'<int>'})
        self.checkStatement("[a,b] = [2,'abc']", {'a':'<int>','b':'<str>'})
    
    def testNestedAssignment(self):
        self.checkStatement("(a,b),c = (1,2),3", {'a':'<int>','b':'<int>','c':'<int>'})
        
    def testMultipleTargetAssignment(self):
        self.checkStatement("a = b = 2", {'a':'<int>','b':'<int>'})
        
    def testReturnValue(self):
        self.checkStatement("return 'abc'",'<str>',field="return")
        self.checkStatement("return 2",'<int>',field="return")
        
    def testMultiLineAssignment(self):
        self.checkStatement("a = 1\nb = 2.0\nc = a+b",{'a':'<int>','b':'<float>','c':'<float>'})
        
    def testAugmentedAssignment(self):
        self.checkStatement("a += 3.0", {'a':'<float>, <int>'}, context = {'a':TypeSet(1)})
        
class TestStatementBlockTypeParser__Functions(TestStatementBlockTypeParser__Base):
    def testBasicFunctionDef(self):
        self.checkStatement("def f(): pass", {'f':'f() -> (None)'})

    def testFunctionReturnsNone(self):
        self.checkStatement("def f(): return None", {'f':'f() -> (None)'})

    def testFunctionReturnsInt(self):
        self.checkStatement("def f(): return 1", {'f':'f() -> (<int>)'})
        
    def testFunctionWithArgs(self):
        self.checkStatement("def f(a, b): pass", {'f':'f(a, b) -> (None)'})

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
        self.checkStatement("class A(object): pass\ninst = A()", {'A':'A','inst':'<A>'})
    
    def testClassAttributeCreation(self):
        stmt = "class A(object): pass\nA.b=1"
        ctx = self.getContext(stmt)
        self.assertEqual(ctx['A'].get_attr('b'),'<int>')
        
    def testClassVariableCreation(self):
        stmt = "class A(object):\n  b=1"
        ctx = self.getContext(stmt)
        self.assertEqual(ctx['A'].get_attr('b'),'<int>')
        
    def testClassVariableDoesNotTransferIntoMethods(self):
        stmt = "class A(object):\n  b=1\n  def test(self, a):\n    return b"
        ctx = self.getContext(stmt)
        self.assertEqual(ctx['A'].get_attr('test'),'test(self, a) -> (Unknown)')
        
    def testClassNameDoesTransferIntoMethods(self):
        stmt = "class A(object):\n  b=1\n  def test(self, a):\n    return A"
        ctx = self.getContext(stmt)
        self.assertEqual(ctx['A'].get_attr('test'),'test(self, a) -> (A)')
        
    def testInstanceMethodCreation(self):
        stmt = "class A(object):\n  def im(self):\n    return self"
        ctx = self.getContext(stmt)
        self.assertEqual(ctx['A'].get_attr('im'),'im(self) -> (<A>)')
        
    def testClassMethodCreation(self):
        stmt = "class A(object):\n  @classmethod\n  def cm(cls):\n    return cls"
        ctx = self.getContext(stmt)
        self.assertEqual(ctx['A'].get_attr('cm'),'cm(cls) -> (A)')

    def testStaticMethodCreation(self):
        stmt = "class A(object):\n  @staticmethod\n  def sm(a):\n    return a"
        ctx = self.getContext(stmt)
        self.assertEqual(ctx['A'].get_attr('sm'),'sm(a) -> (Unknown: a)')
    
