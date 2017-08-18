import unittest
from tested.languages.python3 import ClassType, TypeSet


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
