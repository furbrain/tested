import unittest

from tested.languages.python3 import InferredType, TypeSet

class TestInferredType(unittest.TestCase):
    def testInitWithSimpleVal(self):
        it_num = InferredType(1)
        it_str = InferredType("a")
        self.assertEqual(str(it_num),"int")
        self.assertEqual(str(it_str),"str")
        
    def testInitWithSimpleType(self): 
        it_num = InferredType(int)
        it_str = InferredType(str)
        self.assertEqual(str(it_num),"int")
        self.assertEqual(str(it_str),"str")
        
    def testEquality(self):
        it_num = InferredType(int)
        it_str = InferredType(str)
        self.assertEqual(it_num, it_num)
        self.assertEqual(it_num, int)
        self.assertEqual(it_str, it_str)
        self.assertEqual(it_str, str)
        self.assertNotEqual(it_num, 1)
        self.assertNotEqual(it_str, "a")

    def testInequality(self):        
        it_num = InferredType(int)
        it_str = InferredType(str)
        self.assertNotEqual(it_num, it_str)
        self.assertNotEqual(it_num, str)
        self.assertNotEqual(it_str, it_num)
        self.assertNotEqual(it_str, int)
        
class TestTypeSet(unittest.TestCase):
    def testInitWithSingleVal(self):
        st = TypeSet(1)
        self.assertEqual(str(st),"int")
    
    def testInitWithSingleType(self):
        st = TypeSet(int)
        self.assertEqual(str(st),"int")
    
    def testInitWithSingleInferredType(self):
        st = TypeSet(InferredType(1))
        self.assertEqual(str(st),"int")
        
    def testWithMultipleVals(self):
        st = TypeSet(1,"a")
        self.assertEqual(str(st),"int, str")
        
    def testWithMixedVals(self):
        st = TypeSet(int, "a")
        self.assertEqual(str(st),"int, str")
        
    def testMatches(self):
        st = TypeSet(int, "a")
        self.assertTrue(st.matches((int,float)))
        self.assertTrue(st.matches((str,str)))
        self.assertFalse(st.matches((float,list)))
        
    def testEquality(self):
        self.assertEqual(TypeSet(int), TypeSet(int))
        self.assertEqual(TypeSet(int, float), TypeSet(int, float))
        self.assertEqual(TypeSet(int, float),"float, int")
        
    def testInequality(self):
        self.assertNotEqual(TypeSet(int), TypeSet(float))
        self.assertNotEqual(TypeSet(int, float), TypeSet(int))
        self.assertNotEqual(TypeSet(int, float), "int,float")
        self.assertNotEqual(TypeSet(int),[])

