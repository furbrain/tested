import unittest
import tested.itypes.signatures as signatures
import tested.itypes.builtins as builtins
import tested.itypes.basics as basics
import tested.itypes.compound as compound
import tested.itypes.functions as functions

class TestReadType(unittest.TestCase):
    def setUp(self):
        self.int = builtins.get_type_by_name('<int>')
        self.str = builtins.get_type_by_name('<str>')
        self.float = builtins.get_type_by_name('<float>')
        self.scope = builtins.get_global_scope()

    def testReadTypeSimple(self):
        for i in ('int', 'str', 'bytes', 'float', 'complex', 'bool'):
            self.assertEqual(signatures.read_type(i,self.scope), builtins.get_type_by_name('<{}>'.format(i)))
            self.assertEqual(signatures.read_type(i+' ',self.scope), builtins.get_type_by_name('<{}>'.format(i)))
            self.assertEqual(signatures.read_type(' '+i+' ',self.scope), builtins.get_type_by_name('<{}>'.format(i)))
            self.assertEqual(signatures.read_type(' '+i,self.scope), builtins.get_type_by_name('<{}>'.format(i)))
            
            
    def testReadTypeBad(self):
        with self.assertRaises(AttributeError):
            signatures.read_type('plib',self.scope)
            
    def testReadTypeSet(self):
        self.assertEqual(signatures.read_type('int | str | float',self.scope), basics.TypeSet(self.int, self.str, self.float))
        self.assertEqual(signatures.read_type('int|str|float',self.scope), basics.TypeSet(self.int, self.str, self.float))

    def testReadList(self):
        self.assertEqual(signatures.read_type('[int]',self.scope), compound.InferredList(self.int))

    def testReadComplexList(self):
        self.assertEqual(signatures.read_type('[int | float]',self.scope), compound.InferredList(self.int, self.float))
        
    def testReadNestedList(self):
        self.assertEqual(signatures.read_type('[[int] | float]',self.scope), compound.InferredList(compound.InferredList(self.int), self.float))

    def testReadTuple(self):
        self.assertEqual(signatures.read_type('(int)',self.scope), compound.InferredTuple(self.int))
        
    def testReadComplexTuple(self):
        self.assertEqual(signatures.read_type('(int, float)',self.scope), compound.InferredTuple(self.int, self.float))    
        self.assertNotEqual(signatures.read_type('(float, int)',self.scope), compound.InferredTuple(self.int, self.float))
        
    def testReadDict(self):
        self.assertEqual(signatures.read_type('{int:float}',self.scope), compound.InferredDict([self.int],[self.float]))
        
    def testReadComplexDict(self):
        self.assertEqual(signatures.read_type('{(int):{float}}',self.scope), compound.InferredDict([compound.InferredTuple(self.int)], [compound.InferredSet(self.float)]))
        
    def testReadVeryComplexType(self):
        self.assertEqual(signatures.read_type('(int, {int | float}, [int | str])',self.scope),
            compound.InferredTuple(self.int, compound.InferredSet(self.int, self.float), compound.InferredList(self.int, self.str)))
            
    def testReadBadNesting(self):
        with self.assertRaises(AttributeError):
            signatures.read_type('([int)]',self.scope)
            
class TestReadSpec(unittest.TestCase):
    def setUp(self):
        self.scope = builtins.get_global_scope()

    def testBasicFunction(self):
        self.assertEqual(signatures.read_spec('f()->None\n', self.scope),
                         {'f':functions.FunctionType ('f', [], builtins.get_type_by_value(None), '')})  
         
         
    def testFunctionWithDocstring(self):
        func = signatures.read_spec('f()->None\n  Docs1\n  Docs2\n',self.scope)        
        self.assertEqual(func['f'].docstring,'Docs1\nDocs2')
        
