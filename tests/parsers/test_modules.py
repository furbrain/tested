import unittest
import os.path

from tested.parsers import modules
from tested import scopes

#import logging
#logging.basicConfig(level=logging.DEBUG)

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

fixture_dir = os.path.join(os.path.dirname(__file__),'..','fixtures','fake_project')
main_file = os.path.join(fixture_dir,'main.py')
submod_file = os.path.join(fixture_dir, 'submod', 'submod1.py')

class FakeDocument():
    def __init__(self, location):
        self.location = location
        

class TestModuleType(unittest.TestCase):
    def createModule(self, text, location=""):
        return modules.module_from_text(text, location, FakeDocument(location))

    def checkModule(self, text, result, location=""):
        module = self.createModule(text, location)
        answer = module.scope.context
        for k, v in result.items():
            self.assertEqual(v,answer[k])

    def testSimpleAssignment(self):
        self.checkModule("a = 1",{'a':'<int>'})
        
    def testContingentAssignment(self):
        self.checkModule("a=1\nb=a",{'a':'<int>','b':'<int>'})
        
    def testComplexAssignment(self):
        self.checkModule("a=1\nb=2.5\nc=a*b", {'a': '<int>','b': '<float>','c': '<float>'})
        
    def testSimpleAbsoluteImport(self):
        self.checkModule("import secondary\nx = secondary.x", {'x': '<int>'}, location=main_file)
        
    def testRecursiveModuleImports(self):
        self.checkModule("import recursive_a\nx = recursive_a.recursive_b.f()", {'x': '<int>'}, location=main_file)
    
    def testRelativeFlatImport(self):
        self.checkModule("from . import secondary\nx = secondary.x", {'x': '<int>'}, location=main_file)
        
    def testImportFromParent(self):
        self.checkModule("from .. import secondary\nx = secondary.x", {'x': '<int>'}, location=submod_file)
        
    def testImportAttributeFrom__Init__(self):
        self.checkModule("from . import init_var", {'init_var': '<str>'}, location=submod_file)
        
    def testImportModuleFrom__Init(self):
        self.checkModule("from . import submod2", {'submod2': 'submod2'}, location=submod_file)
        
    def testImportAttributeFromModule(self):
        self.checkModule("from .submod2 import submod2_var", {'submod2_var': '<float>'}, location=submod_file)
        
class TestIndentation(unittest.TestCase):
    def setUpSpecimenModule(self):
        mod = modules.module_from_text(SPECIMEN_CODE, '', None)
        return mod.scope_list
        
    def getScopeStarting(self, scopes, line_start):
        possible_scopes = [x for x in scopes if x.line_start == line_start]
        return possible_scopes[0].get_whole_context()

    def testModuleScope(self):
        scopes = self.setUpSpecimenModule()
        ctx = self.getScopeStarting(scopes, 0)
        self.assertIn('antelope', ctx)
        self.assertIn('late_variable', ctx)
        self.assertIn('simple_function', ctx)
        self.assertIn('BaseClass', ctx)
        self.assertNotIn('local_var_f1', ctx)
        self.assertNotIn('arg1', ctx)
        self.assertNotIn('local_var_f1', ctx)
        self.assertNotIn('subclass_method', ctx)
        self.assertNotIn('SubClass', ctx)
        self.assertNotIn('arg2', ctx)

    def testFuncScope(self):
        scopes = self.setUpSpecimenModule()
        ctx = self.getScopeStarting(scopes, 6)
        self.assertIn('arg1',ctx)
        self.assertIn('antelope',ctx)
        self.assertIn('late_variable',ctx)
        
    def testClassMethodScopeIsComplete(self):
        scopes = self.setUpSpecimenModule()
        ctx = self.getScopeStarting(scopes, 22)
        self.assertTrue('__init__' in ctx['self'].get_all_attrs())
