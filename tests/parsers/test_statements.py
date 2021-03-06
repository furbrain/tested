import unittest
import ast
from tested.parsers.statements import parse_statements
from tested.itypes import TypeSet, ClassType
from tested.scopes import Scope

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
        parse_statements(stmt, scope)
        return scope.get_whole_context()     
        
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
        
    def testMultiLineAssignment(self):
        self.checkStatement("a = 1\nb = 2.0\nc = a+b",{'a':'<int>','b':'<float>','c':'<float>'})
        
    def testAugmentedAssignment(self):
        self.checkStatement("a += 3.0", {'a':'<float> | <int>'}, context = {'a':TypeSet(1)})

    def testForStatement(self):
        self.checkStatement("a = [1,2,3,4]\nfor x in a:\n  y=x+2.1", 
                            {'a':'[<int>]', 'x':'<int>', 'y':'<float>'})
        
    def testWithStatement(self):
        self.checkStatement("class Context:\n  pass\nwith Context() as x:\n  pass", 
                            {'Context':'Context', 'x':'<Context>'})
        
class TestStatementBlockTypeParser__Functions(TestStatementBlockTypeParser__Base):
    def testBasicFunctionWithImplicitNone(self):
        self.checkStatement("def f(): pass", {'f':'f() -> (None)'})

    def testFunctionReturnsNone(self):
        self.checkStatement("def f(): return None", {'f':'f() -> (None)'})

    def testFunctionReturnsSemiImplicitNone(self):
        self.checkStatement("def f(): return", {'f':'f() -> (None)'})
        self.checkStatement("def f():\n  if x:\n    return\n  else:\n    return 1", {'f':'f() -> (<int> | None)'})

    def testFunctionReturnsInt(self):
        self.checkStatement("def f(): return 1", {'f':'f() -> (<int>)'})
        
    def testFunctionWithArgs(self):
        self.checkStatement("def f(a, b): pass", {'f':'f(a, b) -> (None)'})

    def testFunctionReturnsOneArg(self):
        self.checkStatement("def f(a): return a", {'f':'f(a) -> (Unknown: a)'})
        
    def testFunctionWithVarargs(self):
        self.checkStatement("def f(a, *b): return b", {'f':'f(a) -> ([Unknown: b])'})
        
    def testFunctionWithKwArgs(self):
        self.checkStatement("def f(a, **b): return b", {'f':'f(a) -> ({<str>: Unknown})'})
        
    def testFunctonReturnsEitherArg(self):
        func = """
def f(a, b):
    if a:
         return a
    else:
         return b
"""
        self.checkStatement(func, {'f':'f(a, b) -> (Unknown: a | Unknown: b)'})
                
                
class TestStatementBlockTypeParser__Classes(TestStatementBlockTypeParser__Base):
    def testClassCreation(self):
        self.checkStatement("class A(object): pass", {'A':'A'})
        
    def testClassInstanceCreation(self):
        self.checkStatement("class A(object): pass\ninst = A()", {'A':'A','inst':'<A>'})
    
    def testClassAttributeCreation(self):
        stmt = "class A(object): pass\nA.b=1\na=A()"
        ctx = self.getContext(stmt)
        self.assertEqual(ctx['A'].get_attr('b'),'<int>')
        self.assertEqual(ctx['a'].get_attr('b'),'<int>')
        
    def testClassVariableCreation(self):
        stmt = "class A(object):\n  b=1\na=A()"
        ctx = self.getContext(stmt)
        self.assertEqual(ctx['A'].get_attr('b'),'<int>')
        self.assertEqual(ctx['a'].get_attr('b'),'<int>')
        
    def testClassVariableDoesNotTransferIntoMethods(self):
        stmt = "class A(object):\n  b=1\n  def test(self, a):\n    return b\na=A()"
        ctx = self.getContext(stmt)
        self.assertEqual(ctx['A'].get_attr('test'),'test(self, a) -> (Unknown)')
        self.assertEqual(ctx['a'].get_attr('test'),'test(self, a) -> (Unknown)')
        
    def testClassNameDoesTransferIntoMethods(self):
        stmt = "class A(object):\n  b=1\n  def test(self, a):\n    return A\na=A()"
        ctx = self.getContext(stmt)
        self.assertEqual(ctx['A'].get_attr('test'),'test(self, a) -> (A)')
        self.assertEqual(ctx['a'].get_attr('test'),'test(self, a) -> (A)')
        
    def testInstanceMethodCreation(self):
        stmt = "class A(object):\n  def im(self):\n    return self\na=A()"
        ctx = self.getContext(stmt)
        self.assertEqual(ctx['A'].get_attr('im'),'im(self) -> (<A>)')
        self.assertEqual(ctx['a'].get_attr('im'),'im(self) -> (<A>)')
        
    def testClassMethodCreation(self):
        stmt = "class A(object):\n  @classmethod\n  def cm(cls):\n    return cls\na=A()"
        ctx = self.getContext(stmt)
        self.assertEqual(ctx['A'].get_attr('cm'),'cm(cls) -> (A)')
        self.assertEqual(ctx['a'].get_attr('cm'),'cm(cls) -> (A)')

    def testStaticMethodCreation(self):
        stmt = "class A(object):\n  @staticmethod\n  def sm(a):\n    return a\na=A()"
        ctx = self.getContext(stmt)
        self.assertEqual(ctx['A'].get_attr('sm'),'sm(a) -> (Unknown: a)')
        self.assertEqual(ctx['a'].get_attr('sm'),'sm(a) -> (Unknown: a)')
        
    def testStaticMethodWithNoArgsCreation(self):
        stmt = "class A(object):\n  @staticmethod\n  def sm():\n    return 1\na=A()"
        ctx = self.getContext(stmt)
        self.assertEqual(ctx['A'].get_attr('sm'),'sm() -> (<int>)')
        self.assertEqual(ctx['a'].get_attr('sm'),'sm() -> (<int>)')
        
    def testClassInheritance(self):
        stmt = "class A(object):\n  i=1\nclass B(A):\n  s='abc'\na=A()\nb=B()"
        ctx = self.getContext(stmt)
        self.assertEqual(ctx['A'].get_attr('i'),'<int>')
        self.assertEqual(ctx['a'].get_attr('i'),'<int>')
        self.assertEqual(ctx['B'].get_attr('i'),'<int>')
        self.assertEqual(ctx['b'].get_attr('i'),'<int>')
        self.assertFalse(ctx['A'].has_attr('s'))
        self.assertFalse(ctx['a'].has_attr('s'))
        self.assertEqual(ctx['B'].get_attr('s'),'<str>')
        self.assertEqual(ctx['b'].get_attr('s'),'<str>')

        
        
