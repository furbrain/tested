import unittest
from tested.languages.python3.signatures import read_function, read_type
from tested.languages.python3.builtins import get_built_in_type, get_built_in_for_literal
from tested.languages.python3.inferred_types import UnknownType, TypeSet, InferredList, InferredTuple, InferredSet, InferredDict, InferredType
from tested.languages.python3.functions import FunctionType

class TestReadType(unittest.TestCase):
    def setUp(self):
        self.int = get_built_in_type('<int>')
        self.str = get_built_in_type('<str>')
        self.float = get_built_in_type('<float>')

    def testReadTypeSimple(self):
        for i in ('int', 'str', 'bytes', 'float', 'complex', 'bool'):
            self.assertEqual(read_type(i), get_built_in_type('<{}>'.format(i)))
            self.assertEqual(read_type(i+' '), get_built_in_type('<{}>'.format(i)))
            self.assertEqual(read_type(' '+i+' '), get_built_in_type('<{}>'.format(i)))
            self.assertEqual(read_type(' '+i), get_built_in_type('<{}>'.format(i)))
            
            
    def testReadTypeBad(self):
        with self.assertRaises(AttributeError):
            read_type('plib')
            
    def testReadTypeSet(self):
        self.assertEqual(read_type('int | str | float'), TypeSet(self.int, self.str, self.float))
        self.assertEqual(read_type('int|str|float'), TypeSet(self.int, self.str, self.float))

    def testReadList(self):
        self.assertEqual(read_type('[int]'), InferredList(self.int))

    def testReadComplexList(self):
        self.assertEqual(read_type('[int | float]'), InferredList(self.int, self.float))
        
    def testReadNestedList(self):
        self.assertEqual(read_type('[[int] | float]'), InferredList(InferredList(self.int), self.float))

    def testReadTuple(self):
        self.assertEqual(read_type('(int)'), InferredTuple(self.int))
        
    def testReadComplexTuple(self):
        self.assertEqual(read_type('(int, float)'), InferredTuple(self.int, self.float))    
        self.assertNotEqual(read_type('(float, int)'), InferredTuple(self.int, self.float))
        
    def testReadDict(self):
        self.assertEqual(read_type('{int:float}'), InferredDict([self.int],[self.float]))
        
    def testReadComplexDict(self):
        self.assertEqual(read_type('{(int):{float}}'), InferredDict([InferredTuple(self.int)], [InferredSet(self.float)]))
        
    def testReadVeryComplexType(self):
        self.assertEqual(read_type('(int, {int | float}, [int | str])'),
            InferredTuple(self.int, InferredSet(self.int, self.float), InferredList(self.int, self.str)))
            
    def testReadBadNesting(self):
        with self.assertRaises(AttributeError):
            read_type('([int)]')
            
class TestReadFunction(unittest.TestCase):
    def testBasicFunction(self):
        self.assertEqual(read_function('f()->None'), FunctionType ('f',[],get_built_in_for_literal(None),''))  
         
        
