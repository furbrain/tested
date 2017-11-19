import unittest
from tested import scopes

class TestScopeMatches(unittest.TestCase):
    def testBaseScopeMatches(self):
        sc = scopes.Scope('name', line_start=0, indent=-1, line_end=100)
        self.assertTrue(sc.matches(50,0))

    def testIndentedScopeMatches(self):
        sc = scopes.Scope('name', line_start=0, indent=0, line_end=100)
        self.assertTrue(sc.matches(50,4))
        
    def testUnindentedScopeDoesNotMatch(self):    
        sc = scopes.Scope('name', line_start=0, indent=4, line_end=100)
        self.assertFalse(sc.matches(50,0))

    def testOutsideScopeDoesNotMatch(self):
        sc = scopes.Scope('name', line_start=0, indent=0, line_end=10)
        self.assertFalse(sc.matches(50,0))
        
    def testScopeTrees(self):
        sc1 = scopes.Scope('sc1', line_start=0, indent=-1)
        sc2 = scopes.Scope('sc2', line_start=4, indent=0, parent=sc1)
        self.assertIn(sc2,sc1.get_all_children())

class TestScopeList(unittest.TestCase):
    def checkScope(self, scope_list, position, match):
        s = scopes.ScopeList()
        for scope in scope_list:
            s.add(scopes.Scope(*scope))
        result = s.get_scope(*position)
        self.assertEqual(result.context,match)

    def testScopeListFindsSimpleMatch(self):
        dct = {'a':int}
        self.checkScope([('name',0,-1,None,10,dct)], (5,0), dct)

    def testScopeListFindsSimpleIndentedMatch(self):
        dct = {'a':int}
        self.checkScope([('name',0,-1,None,10,dct)], (5,4), dct)
        
    def testScopeListFindsIndentedMatch(self):
        dcta = {'a':int}
        dctb = {'b':float}
        self.checkScope([('name',0,-1,None,10,dcta), ('name',2,0,None,8,dctb)], (5,0), dcta)
        self.checkScope([('name',0,-1,None,10,dcta), ('name',2,0,None,8,dctb)], (5,1), dctb)

    def testScopeListFindsUnIndentedMatch(self):
        dcta = {'a':int}
        dctb = {'b':float}
        self.checkScope([('name',0,-1,None,10,dcta), ('name',2,4,None,8,dctb)], (9,0), dcta)
        
    def testScopeListFailsWithWrongIndent(self):
        s = scopes.ScopeList()
        dcta = {'a':int}
        s.add(scopes.Scope('name',line_start=0, indent=4, line_end=10, context=dcta))
        self.assertIsNone(s.get_scope(5,0))

    def testScopeListFailsOutsideArea(self):
        s = scopes.ScopeList()
        dcta = {'a':int}
        s.add(scopes.Scope('name',line_start=0, indent=4, line_end=10, context=dcta))
        self.assertIsNone(s.get_scope(12,0))
        
