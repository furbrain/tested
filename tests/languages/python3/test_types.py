import unittest

from tested.languages.python3 import InferredType, TypeSet, UnknownType

class TestInferredType(unittest.TestCase):
    def testInitWithSimpleVal(self):
        it_num = InferredType.fromType(1)
        it_str = InferredType.fromType("a")
        self.assertEqual(str(it_num),"int")
        self.assertEqual(str(it_str),"str")
        
    def testInitWithSimpleType(self): 
        it_num = InferredType.fromType(int)
        it_str = InferredType.fromType(str)
        self.assertEqual(str(it_num),"int")
        self.assertEqual(str(it_str),"str")
        
    def testEquality(self):
        it_num = InferredType.fromType(int)
        it_str = InferredType.fromType(str)
        self.assertEqual(it_num, it_num)
        self.assertEqual(it_num, int)
        self.assertEqual(it_str, it_str)
        self.assertEqual(it_str, str)
        self.assertNotEqual(it_num, 1)
        self.assertNotEqual(it_str, "a")

    def testInequality(self):        
        it_num = InferredType.fromType(int)
        it_str = InferredType.fromType(str)
        self.assertNotEqual(it_num, it_str)
        self.assertNotEqual(it_num, str)
        self.assertNotEqual(it_str, it_num)
        self.assertNotEqual(it_str, int)
        
    def testSingleAttributes(self):
        attr_dict = {'int':TypeSet(int),'str':TypeSet(str),'None':TypeSet(None)}
        class TempClass:
            pass
        it = InferredType.fromType(TempClass)
        for name, tp in attr_dict.items():
            it.add_attr(name, tp)
        for name, tp in attr_dict.items():
            self.assertEqual(it.get_attr(name), tp)
         
    def testMultiAttributes(self):
        attr_dict = {'int':TypeSet(int), 'str':TypeSet(str), 'None':TypeSet(None)}
        class TempClass:
            pass
        it = InferredType.fromType(TempClass)
        for tp in attr_dict.values():
            it.add_attr('multi',tp)
        self.assertEqual(it.get_attr('multi'), TypeSet(int,str,None))  
        
    def testUnknownAttribute(self):
        class TempClass:
            pass
        it = InferredType.fromType(TempClass)
        self.assertEqual(it.get_attr('surprise'), TypeSet(UnknownType()))
        
    def testSingleItem(self):
        class TempClass:
            pass
        it = InferredType.fromType(TempClass)
        it.add_item(TypeSet(int))
        self.assertEqual(it.get_item(12), TypeSet(int))

    def testMultiItem(self):
        class TempClass:
            pass
        it = InferredType.fromType(TempClass)
        it.add_item(TypeSet(int))
        it.add_item(TypeSet(str))
        self.assertEqual(it.get_item(12),TypeSet(int,str))
        
    def testUnknownItem(self):
        class TempClass:
            pass
        it = InferredType.fromType(TempClass)
        self.assertEqual(it.get_item(12), TypeSet(UnknownType()))
        
    def testBadCall(self):
       it = InferredType.fromType(int)
       self.assertEqual(it.get_call_return(1), TypeSet(UnknownType()))
    
        
        
class TestTypeSet(unittest.TestCase):
    def testInitWithSingleVal(self):
        st = TypeSet(1)
        self.assertEqual(str(st),"int")
    
    def testInitWithSingleType(self):
        st = TypeSet(int)
        self.assertEqual(str(st),"int")
    
    def testInitWithSingleInferredType(self):
        st = TypeSet(InferredType.fromType(1))
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

