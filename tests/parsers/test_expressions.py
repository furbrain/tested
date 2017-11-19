import unittest
import ast 

from tested.parsers import expressions
from tested import itypes, scopes

class TestExpressionBase(unittest.TestCase):
    def setUp(self):
        self.int = itypes.get_type_by_name('<int>')
        self.str = itypes.get_type_by_name('<str>')
        self.float = itypes.get_type_by_name('<float>')
        
    def getType(self, expr, context=None):
        if context is None:
            context = scopes.Scope('__test__',0,-1)
        return expressions.get_expression_type(expr, context)
        
    def checkExpr(self, expr, result, context=None):
        answer = str(self.getType(expr, context))
        message = "%s should return %s, instead returned %s, context is %s" % (expr, result, answer, context)
        self.assertEqual(answer, result, msg = message)

    def checkHasAttr(self, expr, attr):
        tp = self.getType(expr)
        self.assertTrue(tp.has_attr(attr))
                
class TestSimpleExpressions(TestExpressionBase):
    def testSingleNumber(self):
        self.checkExpr("1","<int>")
        
    def testFloatNumber(self):
        self.checkExpr("1.0","<float>")

    def testPlainString(self):
        self.checkExpr("'abc'","<str>")
        
    def testBytes(self):
        self.checkExpr("b'abc'","<bytes>")          
        
    def testBoolean(self):
        self.checkExpr("True","<bool>")
        self.checkExpr("False","<bool>")
        
    def testNone(self):
        self.checkExpr("None",'None')
    
    def testExpressionWithVariables(self):
        context = {'a':self.float, 'b':self.int}
        self.checkExpr("a","<float>",context=context)
        self.checkExpr("b","<int>",context=context)
    
    def testExpressionWithUnknownVariable(self):
        context = {'a':self.float, 'b':self.int}
        self.checkExpr("c","Unknown", context=context)
        
    
class TestOperations(TestExpressionBase):
    def testNumericBinaryOpConversions(self):
        numbers = [('1','<int>'), ('2.3','<float>')]
        for a,b in numbers:
            for c,d in numbers:
                expr = a + " + " + c
                if '<float>' in (b,d):
                    self.checkExpr(expr, "<float>")
                else:
                    self.checkExpr(expr, "<int>")

    def testStringBinaryOpConversions(self):
        str_tests = ('"abc" * 3', '"abc" + "def"', '"%d" % 1' )
        for expr in str_tests:
            self.checkExpr(expr, '<str>')
            
    def testMixedBinaryConversions(self):
        dct = {'a':itypes.create_list(self.int), 'b':itypes.create_list(self.int, self.str)}
        self.checkExpr("a[0]+b[0]","<int>", context=dct)
        self.checkExpr("b[0]+b[0]","<int> | <str>", context=dct)
        self.checkExpr("a[0]*b[0]","<int>", context=dct)
        self.checkExpr("b[0]*a[0]","<int> | <str>", context=dct)
        
    def testUnaryOps(self):
        boolean_tests = [("not True", "<bool>"), ("not False", "<bool>")]
        for expr,res in boolean_tests:
            self.checkExpr(expr,res)
            
        numeric_tests = [("~ 4", "<int>"), 
                         ("not 4", "<bool>"), 
                         ("- (4.3)","<float>"),
                         ("- True", "<int>")]
        for expr,res in numeric_tests:
            self.checkExpr(expr,res)
        
    def testBooleanOps(self):
        tests = [("True and False", '<bool>'),
                 ("False or False", '<bool>')]
        for expr,res in tests:
            self.checkExpr(expr, res)

    def testCompare(self):
        self.checkExpr("1 < 2", "<bool>")
        self.checkExpr("2 > 3", "<bool>")
        self.checkExpr('"abc" <= "abc"', "<bool>")
        
    def testIfExp(self):
        self.checkExpr("1 if True else 2", "<int>")
        self.checkExpr("1 if False else 'abc'", "<int> | <str>")
    
class TestLists(TestExpressionBase):
    def testListWithSingleType(self):
        self.checkExpr("[1,2,3,4]","[<int>]")
        
    def testListWithMixedTypes(self):
        self.checkExpr("[1,2,'a',3,4]","[<int> | <str>]")
        
    def testListExtraction(self):
        self.checkExpr("[1,2,3,4][0]", "<int>")
        self.checkExpr("[1,2,3,'a',4][0]", "<int> | <str>")
        
    def testListSlice(self):
        self.checkExpr("[1,2,3,4][:]", "[<int>]")
        self.checkExpr("[1,2,3,4][1:]", "[<int>]")
        self.checkExpr("[1,2,3,4][:-1]", "[<int>]")
        
    def testListHasAttributes(self):
        self.checkHasAttr("[1,2,3,4]","append")
    
class TestTuples(TestExpressionBase):
    def testTuple(self):
        self.checkExpr("(1,2,3,4)","(<int>, <int>, <int>, <int>)")
        self.checkExpr("(1,'a')", "(<int>, <str>)")
        
    def testTupleExtraction(self):
        self.checkExpr("(1,'a')[0]", "<int>")
        self.checkExpr("(1,'a')[1]", "<str>")
        
    def testTupleExtractionWithUnknownIndex(self):
        self.checkExpr("(1,'a')[0+1]", "<int> | <str>")
        
    def testTupleSlice(self):
        self.checkExpr("(1,'a',2.0)[1:2]", "[<float> | <int> | <str>]")
        self.checkExpr("(1,'a')[:]", "[<int> | <str>]")
        
    def testTupleConstructionFromStarred(self):
        tp = itypes.create_tuple(self.int, self.float)
        ctx = {'tp':tp}
        self.checkExpr("('abc', *tp)", "(<str>, <int>, <float>)", context=ctx)    

    def testTupleHasAttributes(self):
        self.checkHasAttr("(1,2)","index")

        
class TestDicts(TestExpressionBase):
    def testDict(self):
        self.checkExpr("{1: 'abc', 2.0: [1,2]}", "{<float> | <int>: <str> | [<int>]}")
        
    def testDictIndex(self):
        self.checkExpr("{1: 'abc', 2.0: [1,2]}[1]", "<str> | [<int>]")

    def testDictHasAttributes(self):
        self.checkHasAttr("{1: 'abc', 2.0: [1,2]}","items")

        
class TestSets(TestExpressionBase):
    def testSet(self):
        self.checkExpr("{1, 2, 3}",'{<int>}')
        
    def testMixedSet(self):
        self.checkExpr("{1, 'abc'}", '{<int> | <str>}')
        
    def testSetHasAttributes(self):
        self.checkHasAttr("{1, 2, 3}",'union')
        

class TestFunctions(TestExpressionBase):
    def testSimpleFunctionCall(self):
        f = itypes.FunctionType('f', [], self.int, "")
        context = {'f':f}
        self.checkExpr("f()", "<int>", context=context)
        
    def testContingentFunctionCall(self):
        f = itypes.FunctionType('f', ['a', 'b'], itypes.UnknownType('a'), "")
        context = {'f':f}
        self.checkExpr("f(1, 'str')", "<int>", context=context)

        f = itypes.FunctionType('f', ['a', 'b'], itypes.UnknownType('b'), "")
        context = {'f':f}
        self.checkExpr("f(1, 'str')", "<str>", context=context)
        
    def testComplexContingentFunctionCall(self):
        f = itypes.FunctionType('f', ['a', 'b'], itypes.TypeSet(itypes.UnknownType('a'),itypes.UnknownType('b')), "")
        context = {'f':f}
        self.checkExpr("f(1, 'str')", "<int> | <str>", context=context)
        
    def testUnknownResponse(self):
        f = itypes.FunctionType('f', ['a', 'b'], itypes.TypeSet(itypes.UnknownType('a'),itypes.UnknownType('b')), "")
        context = {'f':f}
        self.checkExpr("f()", "Unknown", context=context)
        
    def testLambdaExpression(self):
        self.checkExpr('lambda x: 3', '__lambda__(x) -> (<int>)')
        
    def getStarredContext(self):    
        f = itypes.FunctionType('f', ['a', 'b'], itypes.UnknownType('b'), "")
        tpl = itypes.create_tuple(self.int, self.float)
        lst = itypes.create_list(self.int, self.str)
        ts = itypes.TypeSet(tpl,lst)
        context = {'f':f, 'lst':lst, 'tpl':tpl, 'ts':ts}
        return context
        
    def testStarredArgumentFunctionCallWithList(self):
        context = self.getStarredContext()
        self.checkExpr("f(*lst)", "<int> | <str>", context=context)
        
    def testStarredArgumentFunctionCallWithTuple(self):
        context = self.getStarredContext()
        self.checkExpr("f(*tpl)", "<float>", context=context)
        
    def testStarredArgumentFunctionCallWithTypeSet(self):
        context = self.getStarredContext()
        self.checkExpr("f(*ts)", "<float> | <int> | <str>", context=context)
        
class TestClasses(TestExpressionBase):
    def testGetAttribute(self):
        c = itypes.ClassType('C',[],'')
        c.add_attr('a',self.int)
        context={'C':c}
        self.checkExpr("C.a", "<int>", context=context)
        
       
class TestComprehensions(TestExpressionBase):
    def testListComprehension(self):
        self.checkExpr("[x for x in [1,2,3]]", '[<int>]')
        self.checkExpr("[x for x in [1,2,3] if x <2]", '[<int>]')
        
    def testListComprehensionWithTuples(self):
        self.checkExpr("[x for x, y in [(1,'a'),(2,'b'),(3,'c')]]", '[<int>]')
        self.checkExpr("[y for x, y in [(1,'a'),(2,'b'),(3,'c')]]", '[<str>]')
        
    def testListComprehensionHasAttributes(self):
        self.checkHasAttr("[x for x in [1,2,3]]","append")

    def testSetComprehension(self):
        self.checkExpr("{x for x in [1,2,3]}", '{<int>}')

    def testSetComprehensionHasAttributes(self):
        self.checkHasAttr("{x for x in [1,2,3]}","union")

    def testDictComprehension(self):
        self.checkExpr("{x:x for x in [1,2,3]}", '{<int>: <int>}')
        self.checkExpr("{x:'a' for x in [1,2,3]}", '{<int>: <str>}')
        
    def testDictComprehensionHasAttributes(self):
        self.checkHasAttr("{x:x for x in [1,2,3]}","items")

    def testGeneratorExpr(self):
        self.checkExpr("(x for x in [1,2,3])", '(-> <int>)')

