import unittest
from tested.languages.python3 import get_global_scope
from tested.languages.python3.magic_functions import FUNC_TYPES, UNKNOWN_FUNCS, REFLEX_FUNCS, get_instance_name_from_type

class BasicTypeBase(unittest.TestCase):
    def setUp(self):
        self.type = get_global_scope()[get_instance_name_from_type(self.target_type)]

    def testExistence(self):
        pass

    def testName(self):
        self.assertEqual(str(self.type),get_instance_name_from_type(self.target_type))


    def testAllAppropriateFunctionsAvailable(self):
        all_funcs = UNKNOWN_FUNCS.split() + REFLEX_FUNCS.split()
        for x in FUNC_TYPES.values():
            all_funcs.extend(x.split())
        all_funcs = ["__{}__".format(x) for x in all_funcs]
        for func in all_funcs:
            with self.subTest(func=func):
                if hasattr(self.target_type, func):
                    self.assertTrue(self.type.has_attr(func))
                
class TestIntLiteral(BasicTypeBase):
    target_type = int

class TestFloatLiteral(BasicTypeBase):
    target_type = float

class TestComplexLiteral(BasicTypeBase):
    target_type = complex

class TestStrLiteral(BasicTypeBase):
    target_type = str

class TestNoneLiteral(BasicTypeBase):
    target_type = type(None)

del BasicTypeBase
