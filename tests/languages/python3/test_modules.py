import unittest
import pprint
import attr
from tested.languages.python3 import ModuleTypeParser, LineNumberGetter

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
        self.member_variable = arg8
                
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
        pprint.pprint(scopes)
        possible_scopes = [x for x in scopes if x.line_start == line_start]
        return possible_scopes[0].get_whole_context()

    def testSimpleAssignment(self):
        self.checkModule("a = 1",{'a':'int'})
        
    def testContingentAssignment(self):
        self.checkModule("a=1\nb=a",{'a':'int','b':'int'})
        
    def testComplexAssignment(self):
        self.checkModule("a=1\nb=2.5\nc=a*b",{'a':'int','b':'float','c':'float'})
        
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
    
