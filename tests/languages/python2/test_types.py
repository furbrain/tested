import unittest

from tested.languages.python2 import InferredType, TypeSet

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
        self.assertTrue(it_num==it_num)
        self.assertTrue(it_num==int)
        self.assertTrue(it_str==it_str)
        self.assertTrue(it_str==str)
        self.assertFalse(it_num==1)
        self.assertFalse(it_str=="a")

    def testInequality(self):        
        it_num = InferredType(int)
        it_str = InferredType(str)
        self.assertFalse(it_num==it_str)
        self.assertFalse(it_num==str)
        self.assertFalse(it_str==it_num)
        self.assertFalse(it_str==int)
        
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
        self.assertEqual(str(st),"int,str")
        
    def testWithMixedVals(self):
        st = TypeSet(int, "a")
        self.assertEqual(str(st),"int,str")
        
    def testMatches(self):
        st = TypeSet(int, "a")
        self.assertTrue(st.matches((int,float)))
        self.assertTrue(st.matches((str,unicode)))
        self.assertFalse(st.matches((float,unicode)))

