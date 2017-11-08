import unittest
from tested.languages.python3.signatures import read_spec, read_type
from tested.languages.python3.builtins import get_built_in_type, get_built_in_for_literal, get_global_scope
from tested.languages.python3.inferred_types import UnknownType, TypeSet, InferredList, InferredTuple, InferredSet, InferredDict, InferredType
from tested.languages.python3.functions import FunctionType

class TestReadType(unittest.TestCase):
    def setUp(self):
        self.int = get_built_in_type('<int>')
        self.str = get_built_in_type('<str>')
        self.float = get_built_in_type('<float>')
        self.scope = get_global_scope()

    def testReadTypeSimple(self):
        for i in ('int', 'str', 'bytes', 'float', 'complex', 'bool'):
            self.assertEqual(read_type(i,self.scope), get_built_in_type('<{}>'.format(i)))
            self.assertEqual(read_type(i+' ',self.scope), get_built_in_type('<{}>'.format(i)))
            self.assertEqual(read_type(' '+i+' ',self.scope), get_built_in_type('<{}>'.format(i)))
            self.assertEqual(read_type(' '+i,self.scope), get_built_in_type('<{}>'.format(i)))
            
            
    def testReadTypeBad(self):
        with self.assertRaises(AttributeError):
            read_type('plib',self.scope)
            
    def testReadTypeSet(self):
        self.assertEqual(read_type('int | str | float',self.scope), TypeSet(self.int, self.str, self.float))
        self.assertEqual(read_type('int|str|float',self.scope), TypeSet(self.int, self.str, self.float))

    def testReadList(self):
        self.assertEqual(read_type('[int]',self.scope), InferredList(self.int))

    def testReadComplexList(self):
        self.assertEqual(read_type('[int | float]',self.scope), InferredList(self.int, self.float))
        
    def testReadNestedList(self):
        self.assertEqual(read_type('[[int] | float]',self.scope), InferredList(InferredList(self.int), self.float))

    def testReadTuple(self):
        self.assertEqual(read_type('(int)',self.scope), InferredTuple(self.int))
        
    def testReadComplexTuple(self):
        self.assertEqual(read_type('(int, float)',self.scope), InferredTuple(self.int, self.float))    
        self.assertNotEqual(read_type('(float, int)',self.scope), InferredTuple(self.int, self.float))
        
    def testReadDict(self):
        self.assertEqual(read_type('{int:float}',self.scope), InferredDict([self.int],[self.float]))
        
    def testReadComplexDict(self):
        self.assertEqual(read_type('{(int):{float}}',self.scope), InferredDict([InferredTuple(self.int)], [InferredSet(self.float)]))
        
    def testReadVeryComplexType(self):
        self.assertEqual(read_type('(int, {int | float}, [int | str])',self.scope),
            InferredTuple(self.int, InferredSet(self.int, self.float), InferredList(self.int, self.str)))
            
    def testReadBadNesting(self):
        with self.assertRaises(AttributeError):
            read_type('([int)]',self.scope)
            
class TestReadSpec(unittest.TestCase):
    def setUp(self):
        self.scope = get_global_scope()

    def testBasicFunction(self):
        self.assertEqual(read_spec('f()->None\n',self.scope),{'f':FunctionType ('f',[],get_built_in_for_literal(None),'')})  
         
         
    def testFunctionWithDocstring(self):
        func = read_spec('f()->None\n  Docs1\n  Docs2\n',self.scope)        
        self.assertEqual(func['f'].docstring,'Docs1\nDocs2')
        
