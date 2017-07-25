import unittest
from tested.languages.python import PythonPlugin
import os

SPECIMEN_CODE = """
#!/usr/bin/env python

import HighlyUseful.Lib
import really.complex.package.name as pkg
from anotherpackage import pkg3
from furtherpackage import pkg6 as pkg4

#random irritating comment mentioning antiquity

antelope = 1000
anteater = "insectivore"

def simple_function(arg1,arg2):
    local_var_f1 = (arg1+
        arg2)
    local_var_f2 = arg1-\
        arg2
    return local_var_f1+local_var_f2
    
class BaseClass(AncestorClass):
    class_level_var = 100
    
    class SubClass:
        def subclass_method(self,arg1,arg3):
            return arg1+arg3
            
    def __init__(self, arg8):
        self.member_variable = arg8
                
    def instance_method(self,arg5,arg6):
        self.contingent_member_variable = arg5
        return arg5-arg6
        
late_variable = 100
b = BaseClass(12)
""" 

class TestPython(unittest.TestCase):
    def testInitWorks(self):
        p = PythonPlugin()

    def testParseWorks(self):
        p = PythonPlugin()
        p.parseText(SPECIMEN_CODE)
