import unittest
import ast 

from tested.languages.python3 import get_expression_type, InferredList, TypeSet, FunctionType, UnknownType, ClassType, get_global_scope

class TestExpressionTypeParser(unittest.TestCase):
    def setUp(self):
        self.int = get_global_scope()['<int>']
        self.str = get_global_scope()['<str>']
        self.float = get_global_scope()['<float>'] 

    def checkExpr(self, expr, result, context=None):
        answer = str(get_expression_type(expr, context))
        message = "%s should return %s, instead returned %s, context is %s" % (expr, result, answer, context)
        self.assertEqual(answer, result, msg = message)
                
    ### SIMPLE CASES ###   
    def testSingleNumber(self):
        self.checkExpr("1","<int>")
        
    def testFloatNumber(self):
        self.checkExpr("1.0","<float>")

    def testPlainString(self):
        self.checkExpr("'abc'","<str>")
        
    def testBoolean(self):
        self.checkExpr("True","<bool>")
        self.checkExpr("False","<bool>")
        
    def testNone(self):
        self.checkExpr("None",'None')
    
    
    ### OPERATIONS ###    
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
        dct = {'a':InferredList(self.int), 'b':InferredList(self.int, self.str)}
        self.checkExpr("a[0]+b[0]","<int>", context=dct)
        self.checkExpr("b[0]+b[0]","<int>, <str>", context=dct)
        self.checkExpr("a[0]*b[0]","<int>", context=dct)
        self.checkExpr("b[0]*a[0]","<int>, <str>", context=dct)
        
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
    
    ### WITH CONTEXT###        
    def testExpressionWithVariables(self):
        context = {'a':self.float, 'b':self.int}
        self.checkExpr("a","<float>",context=context)
        self.checkExpr("b","<int>",context=context)
    
    def testExpressionWithUnknownVariable(self):
        context = {'a':self.float, 'b':self.int}
        self.checkExpr("c","Unknown", context=context)
        
    ### LISTS ###    
    def testListWithSingleType(self):
        self.checkExpr("[1,2,3,4]","[<int>]")
        
    def testListWithMixedTypes(self):
        self.checkExpr("[1,2,'a',3,4]","[<int>, <str>]")
        
    def testListExtraction(self):
        self.checkExpr("[1,2,3,4][0]", "<int>")
        self.checkExpr("[1,2,3,'a',4][0]", "<int>, <str>")
        
    def testListSlice(self):
        self.checkExpr("[1,2,3,4][:]", "[<int>]")
        self.checkExpr("[1,2,3,4][1:]", "[<int>]")
        self.checkExpr("[1,2,3,4][:-1]", "[<int>]")
    
    ### TUPLES ###
    def testTuple(self):
        self.checkExpr("(1,2,3,4)","(<int>, <int>, <int>, <int>)")
        self.checkExpr("(1,'a')", "(<int>, <str>)")
        
    def testTupleExtraction(self):
        self.checkExpr("(1,'a')[0]", "<int>")
        self.checkExpr("(1,'a')[1]", "<str>")
        
    def testTupleSlice(self):
        self.checkExpr("(1,'a',2.0)[1:2]", "[<float>, <int>, <str>]")
        self.checkExpr("(1,'a')[:]", "[<int>, <str>]")
        
    ### DICTS ###
    def testDict(self):
        self.checkExpr("{1: 'abc', 2.0: [1,2]}", "{<float>, <int>: <str>, [<int>]}")
        
    def testDictIndex(self):
        self.checkExpr("{1: 'abc', 2.0: [1,2]}[1]", "<str>, [<int>]")
        
    ### Comparison ###    
    def testCompare(self):
        self.checkExpr("1 < 2", "<bool>")
        self.checkExpr("2 > 3", "<bool>")
        self.checkExpr('"abc" <= "abc"', "<bool>")

    ### FUNCTION CALLS ###
    def testSimpleFunctionCall(self):
        f = FunctionType('f', [], self.int, "")
        context = {'f':f}
        self.checkExpr("f()", "<int>", context=context)
        
    def testContingentFunctionCall(self):
        f = FunctionType('f', ['a', 'b'], UnknownType('a'), "")
        context = {'f':f}
        self.checkExpr("f(1, 'str')", "<int>", context=context)

        f = FunctionType('f', ['a', 'b'], UnknownType('b'), "")
        context = {'f':f}
        self.checkExpr("f(1, 'str')", "<str>", context=context)
        
    def testComplexContingentFunctionCall(self):
        f = FunctionType('f', ['a', 'b'], TypeSet(UnknownType('a'),UnknownType('b')), "")
        context = {'f':f}
        self.checkExpr("f(1, 'str')", "<int>, <str>", context=context)
        
    def testUnknownResponse(self):
        f = FunctionType('f', ['a', 'b'], TypeSet(UnknownType('a'),UnknownType('b')), "")
        context = {'f':f}
        self.checkExpr("f()", "Unknown", context=context)
    
    def testGetAttribute(self):
        c = ClassType('C',[],{},'')
        c.add_attr('a',self.int)
        context={'C':c}
        self.checkExpr("C.a", "<int>", context=context)
        
