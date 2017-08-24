import unittest
from tested.languages.python3 import ClassType, TypeSet, InstanceType, Scope


class TestClasses(unittest.TestCase):
    def makeClass(self, name, parents = None, context=None):
        if parents is None:
            parents = []
        if context is None:
            context = {}
        scope = Scope('',0,0,context=context)
        c = ClassType(name=name, parents=parents, scope=scope, docstring='')
        return c
        
    def testCreateClass(self):
        c = self.makeClass('c')
        
    def testCreateClassWithContext(self):
        c = self.makeClass('c', context = {'i':TypeSet(int)})
        self.assertEqual(c.get_attr('i'),"int")
        
    def testCreateInheritedClassWithContext(self):
        c1 = self.makeClass('c1', context = {'i':TypeSet(int)})
        c2 = self.makeClass('c2',parents = [TypeSet(c1)], context = {'s':TypeSet(str)})
        self.assertEqual(c2.get_attr('i'),"int")        
        self.assertEqual(c2.get_attr('i'),"int")
        
    def testClassCreatesInstance(self):
        c1 = self.makeClass('c1')
        i1 = c1.get_call_return([])
        c2 = self.makeClass('c2')
        i2 = c2.get_call_return([])
        self.assertEqual(i1,TypeSet(InstanceType(c1)))
        self.assertNotEqual(i1,c1)
        self.assertNotEqual(c1,c2)
        self.assertNotEqual(i1,i2)
        
    def testInstanceInheritsContext(self):
        c = self.makeClass('c',context = {'i':TypeSet(int)})
        instance = c.get_call_return([])
        self.assertEqual(instance[0].get_attr('i'),"int")
        
    def testInstancesSameObjects(self):
        c = self.makeClass('c')
        i1 = c.get_call_return([])
        i2 = c.get_call_return([])
        self.assertTrue(i1[0] is i2[0])
