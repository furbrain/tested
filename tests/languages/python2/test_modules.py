import unittest
from tested.languages.python2 import ModuleTypeParser

class TestModuleTypeParser(unittest.TestCase):
    def checkModule(self, module, result, names=None, field="context"):
        if names == None:
            names = {}
        parser = ModuleTypeParser(names)
        parser.parseModule(module)
        answer = getattr(parser,field)
        message = "%s should return %s: %s, instead returned %s, context is %s" % (module, field, result, answer, names)
        self.assertEqual(answer, result)

    def testSimpleAssignment(self):
        self.checkModule("a = 1",{'a':'int'})
        
    def testContingentAssignment(self):
        self.checkModule("a=1\nb=a",{'a':'int','b':'int'})
        
    def testComplexAssignment(self):
        self.checkModule("a=1\nb=2.5\nc=a*b",{'a':'int','b':'float','c':'float'})
