import unittest
from tested.languages.python3.scopes import Scope, ScopeList

class TestScopeMatches(unittest.TestCase):
    def testBaseScopeMatches(self):
        sc = Scope('name', line_start=0, indent=0, line_end=100)
        self.assertTrue(sc.matches(50,0))

    def testIndentedScopeMatches(self):
        sc = Scope('name', line_start=0, indent=0, line_end=100)
        self.assertTrue(sc.matches(50,4))
        
    def testUnindentedScopeDoesNotMatch(self):    
        sc = Scope('name', line_start=0, indent=4, line_end=100)
        self.assertFalse(sc.matches(50,0))

    def testOutsideScopeDoesNotMacth(self):
        sc = Scope('name', line_start=0, indent=0, line_end=10)
        self.assertFalse(sc.matches(50,0))

class TestScopeList(unittest.TestCase):
    def checkScope(self, scope_list, position, match):
        s = ScopeList()
        for scope in scope_list:
            s.add(Scope(*scope))
        result = s.getScope(*position)
        self.assertEqual(result.context,match)

    def testScopeListFindsSimpleMatch(self):
        dct = {'a':int}
        self.checkScope([('name',0,0,None,10,dct)], (5,0), dct)

    def testScopeListFindsSimpleIndentedMatch(self):
        dct = {'a':int}
        self.checkScope([('name',0,0,None,10,dct)], (5,4), dct)
        
    def testScopeListFindsIndentedMatch(self):
        dcta = {'a':int}
        dctb = {'b':float}
        self.checkScope([('name',0,0,None,10,dcta), ('name',2,4,None,8,dctb)], (5,4), dctb)

    def testScopeListFindsUnIndentedMatch(self):
        dcta = {'a':int}
        dctb = {'b':float}
        self.checkScope([('name',0,0,None,10,dcta), ('name',2,4,None,8,dctb)], (9,0), dcta)
        
    def testScopeListFailsWithWrongIndent(self):
        s = ScopeList()
        dcta = {'a':int}
        s.add(Scope('name',line_start=0, indent=4, line_end=10, context=dcta))
        self.assertIsNone(s.getScope(5,0))

    def testScopeListFailsOutsideArea(self):
        s = ScopeList()
        dcta = {'a':int}
        s.add(Scope('name',line_start=0, indent=4, line_end=10, context=dcta))
        self.assertIsNone(s.getScope(12,0))
        
