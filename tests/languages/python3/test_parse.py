import unittest
from tested.languages.python3.parse import get_last_whole_identifier, parse_text, get_suggestions

class TestGetLastWholeIdentifier(unittest.TestCase):
    def checkResponse(self, test, response):
        self.assertEqual(get_last_whole_identifier(test), response)

    def testNullString(self):
        self.checkResponse("","")
        
    def testSimpleString(self):
        self.checkResponse("abc", "abc")
        
    def testUnderscore(self):
        self.checkResponse("a_c", "a_c")    
        
    def testSeparateStrings(self):
        self.checkResponse("abc dek", "dek")
        
    def testAttribute(self):
        self.checkResponse("abc.dek", "abc.dek")
        
    def testUnclosedBracket(self):
        self.checkResponse("abc(de","de")
        
    def testComma(self):
        self.checkResponse("abc(de, fg", "fg")
        
    def testClosedBracket(self):
        self.checkResponse("abc(x, y).dek","abc(x, y).dek")
        
    def testEmptyBracket(self):
        self.checkResponse("abc(","")

    def testUnclosedIndex(self):
        self.checkResponse("abc[de","de")
        
    def testUnclosedSlice(self):
        self.checkResponse("abc[de:fg","fg")

    def testClosedIndex(self):
        self.checkResponse("abc[de]","abc[de]")

    def testClosedSlice(self):
        self.checkResponse("abc[d:e]","abc[d:e]")
        
    def testBinaryOp(self):
        self.checkResponse("abc + dek", "dek")

    def testComplexBinaryOp(self):
        self.checkResponse("abc + dek * fgh < fwi","fwi")

    def testCompareOp(self):
        self.checkResponse("abc < dek", "dek")
        
    def testUnaryOp(self):
        self.checkResponse("-abc", "abc")

    def testComplexCompareOp(self):
        self.checkResponse("abc < dek< fwi", "fwi")

    def testComplexExample(self):
        self.checkResponse("abc()[de:fg].fl", "abc()[de:fg].fl")
        
    def testEndsWithComma(self):
        self.checkResponse('a,', '')
        
    def testEndsWithSpace(self):
        self.checkResponse('abc ', '')
        
    def testEndsWithPeriod(self):
        self.checkResponse('abc.', 'abc.')
