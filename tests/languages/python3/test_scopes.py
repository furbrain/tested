import unittest
from tested.languages.python3.scopes import Scope, ScopeList

class TestScopeMatches(unittest.TestCase):
    def testBaseScopeMatches(self):
        sc = Scope('name',0,100,0,{})
        self.assertTrue(sc.matches(50,0))

    def testIndentedScopeMatches(self):
        sc = Scope('name',0,100,0,{})
        self.assertTrue(sc.matches(50,4))
        
    def testUnindentedScopeDoesNotMatch(self):    
        sc = Scope('name',0,100,4,{})
        self.assertFalse(sc.matches(50,0))

    def testOutsideScopeDoesNotMacth(self):
        sc = Scope('name',0,10,0,{})
        self.assertFalse(sc.matches(50,0))

class TestScopeList(unittest.TestCase):
    def checkScope(self, scope_list, position, match):
        s = ScopeList()
        for scope in scope_list:
            s.addScope(*scope)
        result = s.getScope(*position)
        self.assertEqual(result.context,match)

    def testScopeListFindsSimpleMatch(self):
        dct = {'a':int}
        self.checkScope([('name',0,10,0,dct)], (5,0), dct)

    def testScopeListFindsSimpleIndentedMatch(self):
        dct = {'a':int}
        self.checkScope([('name',0,10,0,dct)], (5,4), dct)
        
    def testScopeListFindsIndentedMatch(self):
        dcta = {'a':int}
        dctb = {'b':float}
        self.checkScope([('name',0,10,0,dcta), ('name',2,8,4,dctb)], (5,4), dctb)

    def testScopeListFindsUnIndentedMatch(self):
        dcta = {'a':int}
        dctb = {'b':float}
        self.checkScope([('name',0,10,0,dcta), ('name',2,8,4,dctb)], (9,0), dcta)
        
    def testScopeListFailsWithWrongIndent(self):
        s = ScopeList()
        dcta = {'a':int}
        s.addScope('name',0,10,4,dcta)
        self.assertIsNone(s.getScope(5,0))

    def testScopeListFailsOutsideArea(self):
        s = ScopeList()
        dcta = {'a':int}
        s.addScope('name',0,10,0,dcta)
        self.assertIsNone(s.getScope(12,0))
        
