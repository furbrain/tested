import unittest

from tested.languages.python3 import assign_to_node, TypeSet, ClassType, InferredList

class TestAssignment(unittest.TestCase):
    def testSimpleAssignment(self):
        context = {}
        assign_to_node('a',TypeSet(int),context)
        self.assertEqual({'a':'int'}, context)
        
    def testClassMemberAssignment(self):
        context = {'C':TypeSet(ClassType('C',[],{},''))}
        assign_to_node('C.x',TypeSet(int),context)
        self.assertEqual(context['C'][0].get_attr('x'), 'int')
        
    def testComplexClassMemberAssignment(self):
        a = ClassType('A',[],{},'')
        a.add_attr('x', TypeSet(int))
        b = ClassType('B',[],{},'')        
        context = {'C':TypeSet(a,b)}
        assign_to_node('C.x',TypeSet(str),context)
        self.assertEqual(a.get_attr('x'),'int, str')
        self.assertEqual(b.get_attr('x'),'str')
        
    def testListIndexAssigment(self):
        """Test assignment to a list index works"""
        context = {'l': TypeSet(InferredList(int))}
        assign_to_node('l[0]',TypeSet(str),context)
        self.assertEqual(context,{'l':'[int, str]'})
        
