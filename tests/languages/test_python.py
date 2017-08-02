import unittest
from tested.languages.python import PythonPlugin, SyntaxTreeVisitor, ExpressionTreeVisitor, getAliasName
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
        
    
class TestExpressionTreeVisitor(unittest.TestCase):
    def checkExpr(self, expr, result, names=None):
        visitor = ExpressionTreeVisitor(names)
        syntax_tree = ast.parse(expr)
        answer = visitor.getType(syntax_tree)
        message = "%s should return %s, instead returned %s, context is %s" % (expr, result, answer, names)
        self.assertEqual(answer, result, msg = message)
        
    def testSingleNumber(self):
        self.checkExpr("1","int")
        
    def testFloatNumber(self):
        self.checkExpr("1.0","float")

    def testLongNumber(self):
        self.checkExpr("1L","long")
     
    def testPlainString(self):
        self.checkExpr("'abc'","str")
        
    def testUnicodeString(self):
        self.checkExpr("u'abc'","unicode")
        
    def testBoolean(self):
        self.checkExpr("True","bool")
        self.checkExpr("False","bool")
        
    def testNone(self):
        self.checkExpr("None",'NoneType')
        
    def testNumericBinaryOpConversions(self):
        numbers = [('1','int'), ('2.3','float'), ('3L','long')]
        for a,b in numbers:
            for c,d in numbers:
                expr = a + " + " + c
                if 'float' in (b,d):
                    self.checkExpr(expr, "float")
                elif 'long' in (b,d):
                    self.checkExpr(expr, "long")
                else:
                    self.checkExpr(expr, "int")

    def testStringBinaryOpConversions(self):
        str_tests = ('"abc" * 3', '"abc" + "def"')
        for expr in str_tests:
            self.checkExpr(expr, 'str')
        unicode_tests = ('u"abc" * 3', '"abc" +u"def"', 'u"abc" + "def"', 'u"abc" + u"def"')
        for expr in unicode_tests:
            self.checkExpr(expr, 'unicode')
        
    def testUnaryOps(self):
        boolean_tests = [("not True", "bool"), ("not False", "bool")]
        for expr,res in boolean_tests:
            self.checkExpr(expr,res)
            
        numeric_tests = [("~ 4", "int"), 
                         ("~4L", "long"), 
                         ("not 4", "bool"), 
                         ("- (4.3)","float"),
                         ("- True", "int")]
        for expr,res in numeric_tests:
            self.checkExpr(expr,res)
        
    def testBooleanOps(self):
        tests = [("True and False", 'bool'),
                 ("False or False", 'bool')]
        for expr,res in tests:
            self.checkExpr(expr, res)
            
    def testExpressionWithVariables(self):
        context = {'a':'float', 'b':'int'}
        self.checkExpr("a","float",names=context)
        self.checkExpr("b","int",names=context)
        self.checkExpr("a+b","float",names=context)
        
