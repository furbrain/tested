import unittest
from tested.languages.python3 import ClassType, TypeSet, InstanceType


class TestClasses(unittest.TestCase):
    def testCreateClass(self):
        c = ClassType('c',[],{},'')
        
    def testCreateClassWithContext(self):
        c = ClassType('c',[],{'i':TypeSet(int)},'')
        self.assertEqual(c.get_attr('i'),"int")
        
    def testCreateInheritedClassWithContext(self):
        c1 = ClassType('c1',[],{'i':TypeSet(int)},'')
        c2 = ClassType('c2',[TypeSet(c1)],{'s':TypeSet(str)},'')
        self.assertEqual(c2.get_attr('i'),"int")        
        self.assertEqual(c2.get_attr('i'),"int")
        
    def testClassCreatesInstance(self):
        c1 = ClassType('c1',[],{},'')
        i1 = c1.get_call_return([])
        c2 = ClassType('c2',[],{},'')
        i2 = c2.get_call_return([])
        self.assertEqual(i1,InstanceType(c1))
        self.assertNotEqual(i1,c1)
        self.assertNotEqual(c1,c2)
        self.assertNotEqual(i1,i2)
