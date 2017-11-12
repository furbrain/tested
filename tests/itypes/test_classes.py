import unittest
import tested.itypes.classes as classes
import tested.itypes.builtins as builtins


class TestClasses(unittest.TestCase):
    def setUp(self):
        self.int = builtins.get_type_by_name('<int>')
        self.str = builtins.get_type_by_name('<str>')


    def makeClass(self, name, parents = None, context=None):
        if parents is None:
            parents = []
        if context is None:
            context = {}
        c = classes.ClassType(name=name, parents=parents, docstring='')
        for k, v in context.items():
            c.add_attr(k, v)
        return c
        
    def testCreateClass(self):
        c = self.makeClass('c')
        
    def testCreateClassWithContext(self):
        c = self.makeClass('c', context = {'i':self.int})
        self.assertEqual(c.get_attr('i'),"<int>")
        
    def testCreateInheritedClassWithContext(self):
        c1 = self.makeClass('c1', context = {'i':self.int})
        c2 = self.makeClass('c2',parents = [c1], context = {'s':self.str})
        self.assertEqual(c2.get_attr('i'),"<int>")        
        self.assertEqual(c2.get_attr('i'),"<int>")
        
    def testClassCreatesInstance(self):
        c1 = self.makeClass('c1')
        i1 = c1.get_call_return([])
        c2 = self.makeClass('c2')
        i2 = c2.get_call_return([])
        self.assertEqual(i1,classes.InstanceType(c1))
        self.assertNotEqual(i1,c1)
        self.assertNotEqual(c1,c2)
        self.assertNotEqual(i1,i2)
        
    def testInstanceInheritsContext(self):
        c = self.makeClass('c',context = {'i':self.int})
        instance = c.get_call_return([])
        self.assertEqual(instance.get_attr('i'),"<int>")
        
    def testInstancesSameObjects(self):
        c = self.makeClass('c')
        i1 = c.get_call_return([])
        i2 = c.get_call_return([])
        self.assertTrue(i1 is i2)
