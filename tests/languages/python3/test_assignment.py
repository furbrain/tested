import unittest

from tested.languages.python3 import assign_to_node, TypeSet, ClassType, InferredList, InferredDict, get_global_scope



class TestAssignment(unittest.TestCase):
    def setUp(self):
        self.int = get_global_scope()['<int>']
        self.str = get_global_scope()['<str>']
        self.float = get_global_scope()['<float>']
        
    def testSimpleAssignment(self):
        context = {}
        assign_to_node('a',TypeSet(self.int),context)
        self.assertEqual({'a':'<int>'}, context)
        
    def testClassMemberAssignment(self):
        context = {'C':TypeSet(ClassType('C',[],''))}
        assign_to_node('C.x',TypeSet(self.int),context)
        self.assertEqual(context['C'][0].get_attr('x'), '<int>')
        
    def testComplexClassMemberAssignment(self):
        a = ClassType('A',[],'')
        a.add_attr('x', TypeSet(self.int))
        b = ClassType('B',[],'')        
        context = {'C':TypeSet(a,b)}
        assign_to_node('C.x',TypeSet(self.str),context)
        self.assertEqual(a.get_attr('x'),'<int>, <str>')
        self.assertEqual(b.get_attr('x'),'<str>')
        
    def testListIndexAssigment(self):
        """Test assignment to a list index works"""
        context = {'l': TypeSet(InferredList(self.int))}
        assign_to_node('l[0]', self.str, context)
        self.assertEqual(context,{'l':'[<int>, <str>]'})
        
    def testListSliceAssignment(self):
        context = {'l': TypeSet(InferredList(self.int))}
        l2 = TypeSet(InferredList(self.str))
        assign_to_node('l[1:2]',l2,context)
        self.assertEqual(context,{'l':'[<int>, <str>]'})
        
    def testListSliceTotalAssignment(self):        
        context = {'l': TypeSet(InferredList(self.int))}
        l2 = TypeSet(InferredList(self.str))
        assign_to_node('l[:]',l2,context)
        self.assertEqual(context,{'l':'[<int>, <str>]'})

    def testDictIndexAssignment(self):
        context = {'d': InferredDict([self.str],[self.int])}
        assign_to_node("d['abc']", self.float, context)
        self.assertEqual(context,{'d':'{<str>: <float>, <int>}'})
        
    def testCallResultAssignmentDoesNothing(self):
        context = {'l': self.int}
        assign_to_node('l()',self.str,context)
        self.assertEqual(context,{'l':'<int>'})
    

