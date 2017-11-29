import unittest

from tested import itypes, parsers
from tested.parsers import assignment
#from tested.languages.python3 import assignment.assign_to_node, itypes.TypeSet, itypes.ClassType, itypes.create_list, itypes.create_tuple, itypes.create_dict, get_global_scope



class TestAssignment(unittest.TestCase):
    def setUp(self):
        self.int = itypes.get_type_by_name('<int>')
        self.str = itypes.get_type_by_name('<str>')
        self.float = itypes.get_type_by_name('<float>')
        
    def testSimpleAssignment(self):
        context = {}
        assignment.assign_to_node('a',itypes.TypeSet(self.int),context)
        self.assertEqual({'a':'<int>'}, context)
        
    def testClassMemberAssignment(self):
        context = {'C':itypes.TypeSet(itypes.ClassType('C',[],''))}
        assignment.assign_to_node('C.x',itypes.TypeSet(self.int),context)
        self.assertEqual(context['C'].get_attr('x'), '<int>')
        
    def testComplexClassMemberAssignment(self):
        a = itypes.ClassType('A',[],'')
        a.add_attr('x', itypes.TypeSet(self.int))
        b = itypes.ClassType('B',[],'')        
        context = {'C':itypes.TypeSet(a,b)}
        assignment.assign_to_node('C.x',itypes.TypeSet(self.str),context)
        self.assertEqual(a.get_attr('x'),'<int> | <str>')
        self.assertEqual(b.get_attr('x'),'<str>')
        
    def testListIndexAssigment(self):
        """Test assignment to a list index works"""
        context = {'l': itypes.TypeSet(itypes.create_list(self.int))}
        assignment.assign_to_node('l[0]', self.str, context)
        self.assertEqual(context,{'l':'[<int> | <str>]'})
        
    def testListSliceAssignment(self):
        context = {'l': itypes.TypeSet(itypes.create_list(self.int))}
        l2 = itypes.TypeSet(itypes.create_list(self.str))
        assignment.assign_to_node('l[1:2]',l2,context)
        self.assertEqual(context,{'l':'[<int> | <str>]'})
        
    def testListSliceTotalAssignment(self):        
        context = {'l': itypes.TypeSet(itypes.create_list(self.int))}
        l2 = itypes.TypeSet(itypes.create_list(self.str))
        assignment.assign_to_node('l[:]',l2,context)
        self.assertEqual(context,{'l':'[<int> | <str>]'})

    def testDictIndexAssignment(self):
        context = {'d': itypes.create_dict([self.str],[self.int])}
        assignment.assign_to_node("d['abc']", self.float, context)
        self.assertEqual(context,{'d':'{<str>: <float> | <int>}'})
        
    def testCallResultAssignmentDoesNothing(self):
        context = {'l': self.int}
        assignment.assign_to_node('l()',self.str,context)
        self.assertEqual(context,{'l':'<int>'})
    
    def testMultipleAssignmentFromList(self):
        context = {}
        mylist = itypes.create_list(self.int, self.str)
        assignment.assign_to_node('a, b', mylist, context)
        self.assertEqual(context, {'a':'<int> | <str>', 'b':'<int> | <str>'})

    def testMultipleAssignmentFromTuple(self):
        context = {}
        mytuple = itypes.create_tuple(self.int, self.str)
        assignment.assign_to_node('a, b', mytuple, context)
        self.assertEqual(context, {'a':'<int>', 'b':'<str>'})
        
    def testAssignmentToStarredFromTuple(self):
        context = {}
        mytuple = itypes.create_tuple(self.int, self.str, self.float)    
        assignment.assign_to_node('(a, *b)', mytuple, context)
        self.assertEqual(context, {'a':'<int>', 'b':'[<float> | <str>]'})

    def testAssignmentToStarredFromList(self):
        context = {}
        mytuple = itypes.create_list(self.int, self.str, self.float)    
        assignment.assign_to_node('(a, *b)', mytuple, context)
        self.assertEqual(context, {'a':'<float> | <int> | <str>', 'b':'[<float> | <int> | <str>]'})


