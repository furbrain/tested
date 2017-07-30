import unittest
from tested.languages.python import PythonPlugin, SyntaxTreeVisitor, getAliasName
import os
import ast
import collections

SPECIMEN_CODE = """
#!/usr/bin/env python

import HighlyUseful.Lib
import really.complex.package.name as pkg
from anotherpackage import pkg3
from furtherpackage import pkg6 as pkg4

#random irritating comment mentioning antiquity

antelope = 1000
anteater = "insectivore"

buzzard, beagle = "bird", "dog"

def simple_function(arg1,arg2=None,*arg3,**arg4):
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

class TestPython(unittest.TestCase):
    def setUp(self):
        self.plugin = PythonPlugin()
        self.plugin.parseText(SPECIMEN_CODE)
        
    def testSetupWorks(self):
        pass
        
    def testNoCandidatesForSecondLine(self):
        self.assertEqual([],self.plugin.getCandidates(1,""))
    
    @unittest.skip("Skip this for now")   
    def testFirstImportIdentified(self):
        self.assertEqual(["HighlyUseful"],self.plugin.getCandidates(2,""))
        
class TestSyntaxTreeVisitor(unittest.TestCase):
    def setUp(self):
        self.parse_tree = ast.parse(SPECIMEN_CODE)
        self.visitor = SyntaxTreeVisitor()
        
    def testSimpleImportWorks(self):
        names = [x.name for x in self.visitor.getEntities(self.parse_tree)]
        self.assertIn("HighlyUseful.Lib",names)
        
    def testImportAs(self):
        names = [x.name for x in self.visitor.getEntities(self.parse_tree)]
        self.assertIn("pkg",names)

    def testFrom(self):
        names = [x.name for x in self.visitor.getEntities(self.parse_tree)]
        self.assertIn("pkg3",names)

    def testFromAs(self):
        names = [x.name for x in self.visitor.getEntities(self.parse_tree)]
        self.assertIn("pkg4",names)
        
    def testSimpleAssignment(self):
        names = [x.name for x in self.visitor.getEntities(self.parse_tree)]
        self.assertIn("antelope",names)
        self.assertIn("anteater",names)
        self.assertNotIn("antiquity",names)
    
    def testMultipleAssignment(self):
        names = [x.name for x in self.visitor.getEntities(self.parse_tree)]
        self.assertIn("buzzard",names)
        self.assertIn("beagle",names)
        
    def testFunctionName(self):
        names = [x.name for x in self.visitor.getEntities(self.parse_tree)]
        self.assertIn("simple_function",names)
        
    def testFunctionArgs(self):
        names = [x.name for x in self.visitor.getEntities(self.parse_tree)]
        self.assertIn("arg1",names)
        self.assertIn("arg2",names)
        self.assertIn("arg3",names)
        self.assertIn("arg4",names)
        
    def testLocalFunctionVars(self):
        names = [x.name for x in self.visitor.getEntities(self.parse_tree)]
        self.assertIn("local_var_f1",names)
        self.assertIn("local_var_f2",names)
    
    
        
class TestGetAliasName(unittest.TestCase):
    AliasMock = collections.namedtuple("AliasMock", "name asname")
    def testSimpleCase(self):
        sample = self.AliasMock("right",None)
        self.assertEqual(getAliasName(sample),"right")
        
    def testAliasCase(self):
        sample = self.AliasMock("wrong","right")
        self.assertEqual(getAliasName(sample),"right")
        
    
    
