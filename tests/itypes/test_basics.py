import unittest
import tested.itypes.basics as basics
import tested.itypes.compound as compound
import tested.itypes.functions as functions

class TestInferredType(unittest.TestCase):
    def setUp(self):
        class TempClass:
            pass
        self.test_type = basics.InferredType.from_type(TempClass)
        
    def testInitWithSimpleVal(self):
        it_num = basics.InferredType.from_type(1)
        it_str = basics.InferredType.from_type("a")
        self.assertEqual(str(it_num),"<int>")
        self.assertEqual(str(it_str),"<str>")
        
    def testInitWithSimpleType(self): 
        it_num = basics.InferredType.from_type(int)
        it_str = basics.InferredType.from_type(str)
        self.assertEqual(str(it_num),"int")
        self.assertEqual(str(it_str),"str")
        
    def testEquality(self):
        it_num = basics.InferredType.from_type(int)
        it_str = basics.InferredType.from_type(str)
        self.assertEqual(it_num, it_num)
        self.assertEqual(it_num, int)
        self.assertEqual(it_str, it_str)
        self.assertEqual(it_str, str)
        self.assertNotEqual(it_num, 1)
        self.assertNotEqual(it_str, "a")

    def testInequality(self):        
        it_num = basics.InferredType.from_type(int)
        it_str = basics.InferredType.from_type(str)
        self.assertNotEqual(it_num, it_str)
        self.assertNotEqual(it_num, str)
        self.assertNotEqual(it_str, it_num)
        self.assertNotEqual(it_str, int)
        
    def testSingleAttributes(self):
        attr_dict = {'int':basics.TypeSet(int),'str':basics.TypeSet(str),'None':basics.TypeSet(None)}
        for name, tp in attr_dict.items():
            self.test_type.add_attr(name, tp)
        for name, tp in attr_dict.items():
            self.assertEqual(self.test_type.get_attr(name), tp)
         
    def testMultiAttributes(self):
        attr_dict = {'int':basics.TypeSet(int), 'str':basics.TypeSet(str), 'None':basics.TypeSet(None)}
        for tp in attr_dict.values():
            self.test_type.add_attr('multi',tp)
        self.assertEqual(self.test_type.get_attr('multi'), basics.TypeSet(int,str,None))  
        
    def testUnknownAttribute(self):
        self.assertEqual(self.test_type.get_attr('surprise'), basics.TypeSet(basics.UnknownType()))
            
    def testCallVia__call__(self):
        func = functions.FunctionType('test',[],basics.TypeSet(int),'')
        self.test_type.set_attr('__call__',func)
        self.assertEqual(self.test_type.get_call_return([]),basics.TypeSet(int))
        
    def testBadCall(self):
        self.assertEqual(self.test_type.get_call_return([]), basics.TypeSet(basics.UnknownType()))

    def testAddType(self):    
        it_num = basics.InferredType.from_type(1)
        it_num2  = basics.InferredType.from_type(2)
        it_str = basics.InferredType.from_type("a")
        self.assertEqual(it_num,it_num.add_type(it_num2))
        self.assertNotEqual(it_num, it_num.add_type(it_str))
        
    def testGetAllAttrs(self):
        it_num = basics.InferredType.from_type(1)
        it_str = basics.InferredType.from_type("a")
        self.test_type.add_attr('a',it_num)
        self.test_type.add_attr('b',it_str)
        self.test_type.add_attr('c',it_num)
        self.test_type.add_attr('c',it_str)
        self.assertEqual(self.test_type.get_all_attrs(),{'a':'<int>', 'b':'<str>', 'c':'<int> | <str>'})
       
       
        

class TestTypeSet(unittest.TestCase):
    def setUp(self):
        class TempClass1:
            pass
        class TempClass2:
            pass
        self.tc1 = basics.InferredType.from_type(TempClass1)    
        self.tc2 = basics.InferredType.from_type(TempClass2)    
        self.multiple_types = basics.TypeSet(self.tc1, self.tc2)
        self.l1 = compound.InferredList()
        self.l2 = compound.InferredList()
        self.multiple_lists = basics.TypeSet(self.l1, self.l2)
        self.int = basics.InferredType.from_type(int)
        self.str = basics.InferredType.from_type(str)

    def testInitWithSingleVal(self):
        st = basics.TypeSet(1)
        self.assertEqual(str(st),"<int>")
    
    def testInitWithSingleType(self):
        st = basics.TypeSet(int)
        self.assertEqual(str(st),"int")
    
    def testInitWithSingleInferredType(self):
        st = basics.TypeSet(basics.InferredType.from_type(1))
        self.assertEqual(str(st),"<int>")
        
    def testWithMultipleVals(self):
        st = basics.TypeSet(1,"a")
        self.assertEqual(str(st),"<int> | <str>")
        
    def testWithMixedVals(self):
        st = basics.TypeSet(int, "a")
        self.assertEqual(str(st),"<str> | int")
        
    def testEquality(self):
        self.assertEqual(basics.TypeSet(int), basics.TypeSet(int))
        self.assertEqual(basics.TypeSet(int, float), basics.TypeSet(int, float))
        self.assertEqual(basics.TypeSet(int, float),"float | int")
        
    def testInequality(self):
        self.assertNotEqual(basics.TypeSet(int), basics.TypeSet(float))
        self.assertNotEqual(basics.TypeSet(int, float), basics.TypeSet(int))
        self.assertNotEqual(basics.TypeSet(int, float), "int | float")
        self.assertNotEqual(basics.TypeSet(int),[])

    def testGetAttr(self): 
        self.tc1.add_attr('tst',self.int)
        self.tc2.add_attr('tst',self.str)
        self.assertEqual(self.multiple_types.get_attr('tst'), basics.TypeSet(self.int, self.str))

    def testAddAttr(self): 
        self.multiple_types.add_attr('tst', self.int)
        self.assertEqual(self.tc1.get_attr('tst'), self.int)
        self.assertEqual(self.tc2.get_attr('tst'), self.int)
        
    def testGetItem(self):
        self.l1.add_item(self.int)
        self.l2.add_item(self.str)
        self.assertEqual(self.multiple_lists.get_item(1), basics.TypeSet(self.int, self.str))

    def testAddItem(self): 
        self.multiple_lists.add_item(self.int)
        self.assertEqual(self.l1.get_item(1),self.int)
        self.assertEqual(self.l2.get_item(1),self.int)

    def testGetCallReturn(self): 
        func1 = functions.FunctionType('f1',[],self.int,'')
        func2 = functions.FunctionType('f2',[],self.str,'')
        ts = basics.TypeSet(func1, func2)
        self.assertEqual(ts.get_call_return([]), basics.TypeSet(self.int, self.str))

    def testGetAllAttrs(self): 
        self.tc1.add_attr('a',self.int)
        self.tc2.add_attr('b',self.str)
        self.tc1.add_attr('c',self.int)
        self.tc2.add_attr('c',self.str)
        self.assertEqual(self.multiple_types.get_all_attrs(),{
            'a':self.int, 
            'b':self.str, 
            'c':basics.TypeSet(self.int, self.str)})

    def testGetIter(self):
        ts = basics.TypeSet(compound.InferredList(self.int),self.int)
        self.assertEqual(ts.get_iter(),'Unknown | int')
        ts = basics.TypeSet(compound.InferredList(self.int), compound.InferredList(self.str))
        self.assertEqual(ts.get_iter(),'int | str')        
