import unittest
import ast 

from tested.languages.python2 import ExpressionTypeParser, InferredList, TypeSet

class TestExpressionTypeParser(unittest.TestCase):
    def checkExpr(self, expr, result, names=None):
        answer = str(self.getType(expr, names))
        message = "%s should return %s, instead returned %s, context is %s" % (expr, result, answer, names)
        self.assertEqual(answer, result, msg = message)
        
    def getType(self, expr, names=None):    
        parser = ExpressionTypeParser(names)
        syntax_tree = ast.parse(expr)
        return parser.getType(syntax_tree)
        
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
        str_tests = ('"abc" * 3', '"abc" + "def"', '"%d" % 1' )
        for expr in str_tests:
            self.checkExpr(expr, 'str')
        unicode_tests = ('u"abc" * 3', '"abc" +u"def"', 'u"abc" + "def"', 'u"abc" + u"def"')
        for expr in unicode_tests:
            self.checkExpr(expr, 'unicode')   
            
    def testMixedBinaryConversions(self):
        dct = {'a':InferredList(int), 'b':InferredList(int,str)}
        self.checkExpr("a[0]+b[0]","int", names=dct)
        self.checkExpr("b[0]+b[0]","int,str", names=dct)
        self.checkExpr("a[0]*b[0]","int", names=dct)
        self.checkExpr("b[0]*a[0]","int,str", names=dct)
        
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
        context = {'a':TypeSet(float), 'b':TypeSet(int)}
        self.checkExpr("a","float",names=context)
        self.checkExpr("b","int",names=context)
        
    def testListWithSingleType(self):
        self.checkExpr("[1,2,3,4]","[int]")
        
    def testListWithMixedTypes(self):
        self.checkExpr("[1,2,'a',3,4]","[int,str]")
        
    def testListExtraction(self):
        self.checkExpr("[1,2,3,4][0]", "int")
        self.checkExpr("[1,2,3,'a',4][0]", "int,str")
        
    def testCompare(self):
        self.checkExpr("1 < 2", "bool")
        self.checkExpr("2 > 3", "bool")
        self.checkExpr('"abc" <= "abc"', "bool")

