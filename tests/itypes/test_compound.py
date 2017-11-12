import unittest
import tested.itypes.basics as basics
import tested.itypes.compound as compound

class TestInferredTuple(unittest.TestCase):
    def setUp(self):
        self.int = basics.InferredType.from_type(int)
        self.str = basics.InferredType.from_type(str)
        self.float = basics.InferredType.from_type(float)
        self.tuple = compound.InferredTuple(self.int, self.str, self.float)
        
    def testInit(self):
        self.assertEqual(self.tuple, '(int, str, float)')
        
    def testIndex(self):
        self.assertEqual(self.tuple.get_item(0), self.int)
        self.assertEqual(self.tuple.get_item(1), self.str)
        self.assertEqual(self.tuple.get_item(2), self.float)
        self.assertEqual(self.tuple.get_item(self.int), basics.TypeSet(self.int, self.str, self.float))
        
    def testBadIndex(self):
        self.assertEqual(self.tuple.get_item(3), basics.UnknownType())    
        
    def testSlice(self):
        self.assertEqual(self.tuple.get_slice(), ['int', 'str', 'float'])
        
    def testSliceFrom(self):
        self.assertEqual(self.tuple.get_slice_from(1), ['str', 'float'])

    def testAddItemDoesNothing(self):
        self.tuple.add_item(basics.InferredType.from_type(complex))
        self.assertEqual(self.tuple, '(int, str, float)') 

    def testGetIter(self):
        self.assertEqual(self.tuple.get_iter(),'float | int | str')
        tpl = compound.InferredTuple(self.int, self.str)

        
class TestInferredList(unittest.TestCase):
    def setUp(self):
        self.int = basics.InferredType.from_type(int)
        self.str = basics.InferredType.from_type(str)
        self.float = basics.InferredType.from_type(float)

    def testCreation(self):
        lst = compound.InferredList(self.int,self.float)
        self.assertEqual(lst, '[float | int]')
        
    def testRecursiveList(self):
        lst = compound.InferredList(self.int)
        lst.add_item(lst)
        self.assertEqual(lst, '[[...] | int]')
        
    def testGetIter(self):
        lst = compound.InferredList(self.int)
        self.assertEqual(lst.get_item(0),lst.get_iter())

    def testSingleItem(self):
        lst = compound.InferredList()
        lst.add_item(basics.TypeSet(int))
        self.assertEqual(lst.get_item(12), basics.TypeSet(int))

    def testMultiItem(self):
        lst = compound.InferredList()
        lst.add_item(basics.TypeSet(int))
        lst.add_item(basics.TypeSet(str))
        self.assertEqual(lst.get_item(12),basics.TypeSet(int,str))
        
    def testUnknownItem(self):
        lst = compound.InferredList()
        self.assertEqual(lst.get_item(12), basics.TypeSet())

            
class TestInferredDIct(unittest.TestCase):
    def setUp(self):
        self.int = basics.InferredType.from_type(int)
        self.str = basics.InferredType.from_type(str)
        self.float = basics.InferredType.from_type(float)
        self.dict = compound.InferredDict(keys = [self.int, self.float], values = [self.str, self.float])

    def testInit(self):
        self.assertEqual(self.dict, '{float | int: float | str}')
        
    def testValues(self):
        self.assertEqual(self.dict.get_item(0), 'float | str')

    def testKeys(self):
        self.assertEqual(self.dict.get_key(), 'float | int')

    def testGetIter(self):
        self.assertEqual(self.dict.get_iter(),'float | int')

