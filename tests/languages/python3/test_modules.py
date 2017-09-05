import unittest
import attr
from tested.languages.python3 import ModuleTypeParser, LineNumberGetter, Scope

SPECIMEN_CODE = """
#!/usr/bin/env python
antelope = 1000
anteater = "insectivore"
buzzard, beagle = "bird", "dog"
def simple_function(arg1,arg2=None,*arg3):
    local_var_f1 = (arg1+
        arg2)
    local_var_f2 = arg1-\
        arg2
    return local_var_f1+local_var_f2
    
class BaseClass(AncestorClass):
    class_level_var = 100
    
    class SubClass:
        def subclass_method(self,arg5,arg6):
            return arg5+arg6
            
    def __init__(self, arg7):
        self.member_variable = arg7
                
    def instance_method(self,arg8,arg9):
        self.contingent_member_variable = arg8
        return arg8-arg9
        
late_variable = 100
b = BaseClass(12)
""" 

class TestModuleTypeParser(unittest.TestCase):
    def checkModule(self, module, result):
        parser = ModuleTypeParser()
        parser.parseModule(module)
        answer = parser.scope.context
        message = "%s should return %s, instead returned %s" % (module, result, answer)
        self.assertEqual(answer, result)


    def setUpSpecimenModule(self):
        parser = ModuleTypeParser()
        return parser.parseModule(SPECIMEN_CODE)
        
    def getScopeStarting(self, scopes, line_start):
        possible_scopes = [x for x in scopes if x.line_start == line_start]
        return possible_scopes[0].get_whole_context()

    def testSimpleAssignment(self):
        self.checkModule("a = 1",{'a':'<int>'})
        
    def testContingentAssignment(self):
        self.checkModule("a=1\nb=a",{'a':'<int>','b':'<int>'})
        
    def testComplexAssignment(self):
        self.checkModule("a=1\nb=2.5\nc=a*b",{'a':'<int>','b':'<float>','c':'<float>'})
        
    def testModuleScope(self):
        scopes = self.setUpSpecimenModule()
        ctx = self.getScopeStarting(scopes, 0)
        self.assertIn('antelope',ctx)
        self.assertIn('late_variable',ctx)
        self.assertIn('simple_function',ctx)
        self.assertIn('BaseClass',ctx)
        self.assertNotIn('local_var_f1',ctx)
        self.assertNotIn('arg1',ctx)
        self.assertNotIn('local_var_f1',ctx)
        self.assertNotIn('subclass_method',ctx)
        self.assertNotIn('SubClass',ctx)
        self.assertNotIn('arg2',ctx)

    def testFuncScope(self):
        scopes = self.setUpSpecimenModule()
        ctx = self.getScopeStarting(scopes, 6)
        self.assertIn('arg1',ctx)
        self.assertIn('antelope',ctx)
        self.assertIn('late_variable',ctx)
        
    def testFindFullScopes(self):
        #a = 1
        #def b(f):
        #    pass
        #c=2
        scope_list = [Scope('__main__',0,0, line_end=4), Scope('def',2,0)]
        lines = [(0,0),(1,0),(2,4),(3,0)]
        parser=ModuleTypeParser()
        new_scopes = list(parser.find_full_scopes(scope_list, lines, 4))
        self.assertEqual(new_scopes[1].line_end,3)

    def testFindFullScopesHangingScope(self):
        #a = 1
        #def b(f):
        #    pass
        scope_list = [Scope('__main__',0,0, line_end=3), Scope('def',2,0)]
        lines = [(0,0),(1,0),(2,4)]
        parser=ModuleTypeParser()
        new_scopes = list(parser.find_full_scopes(scope_list, lines, 3))
        self.assertEqual(new_scopes[1].line_end,3)

    def testClassMethodScopeIsComplete(self):
        scopes = self.setUpSpecimenModule()
        ctx = self.getScopeStarting(scopes, 22)
        self.assertTrue('__init__' in ctx['self'].get_all_attrs())

            
class TestLineNumberGetter(unittest.TestCase):
    def checkLineNumbers(self, text, expected):
        result = LineNumberGetter.get_lines(text)          
        self.assertEqual(result, expected)
        
    def testSimpleAssignment(self):
        self.checkLineNumbers("a = 1",[(1,0)])
        
    def testMultipleAssignment(self):
        self.checkLineNumbers("a = 1\nb = 2",[(1,0),(2,0)])
    
    def testSingleNested(self):
        self.checkLineNumbers("def f(a):\n  return a",[(1,0),(2,2)])
        
    def testNestedFuncs(self):
        self.checkLineNumbers("def f(a,b):\n  def g(b):\n    return a",[(1,0),(2,2),(3,4)])
    
