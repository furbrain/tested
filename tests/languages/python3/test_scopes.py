import unittest
from tested.languages.python3.scopes import Scope, ScopeList

class TestScopeMatches(unittest.TestCase):
    def testBaseScopeMatches(self):
        sc = Scope('name', line_start=0, indent=-1, line_end=100)
        self.assertTrue(sc.matches(50,0))

    def testIndentedScopeMatches(self):
        sc = Scope('name', line_start=0, indent=0, line_end=100)
        self.assertTrue(sc.matches(50,4))
        
    def testUnindentedScopeDoesNotMatch(self):    
        sc = Scope('name', line_start=0, indent=4, line_end=100)
        self.assertFalse(sc.matches(50,0))

    def testOutsideScopeDoesNotMatch(self):
        sc = Scope('name', line_start=0, indent=0, line_end=10)
        self.assertFalse(sc.matches(50,0))
        
    def testScopeTrees(self):
        sc1 = Scope('sc1', line_start=0, indent=-1)
        sc2 = Scope('sc2', line_start=4, indent=0, parent=sc1)
        self.assertIn(sc2,sc1.get_all_children())

class TestScopeList(unittest.TestCase):
    def checkScope(self, scope_list, position, match):
        s = ScopeList()
        for scope in scope_list:
            s.add(Scope(*scope))
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
        s = ScopeList()
        dcta = {'a':int}
        s.add(Scope('name',line_start=0, indent=4, line_end=10, context=dcta))
        self.assertIsNone(s.get_scope(5,0))

    def testScopeListFailsOutsideArea(self):
        s = ScopeList()
        dcta = {'a':int}
        s.add(Scope('name',line_start=0, indent=4, line_end=10, context=dcta))
        self.assertIsNone(s.get_scope(12,0))
        
