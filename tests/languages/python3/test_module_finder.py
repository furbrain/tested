import unittest
import importlib.util
import tested.languages.python3.module_finder as mf


class TestModuleFinder(unittest.TestCase):
    def setUp(self):
        self.files = [
            '/',
            '/home/',
            '/home/test/',
            '/home/test/Project/',
            '/home/test/Project/setup.py',
            '/home/test/Project/project/',
            '/home/test/Project/project/__init__.py',
            '/home/test/Project/project/main.py',
            '/home/test/Project/project/secondary.py',
            '/home/test/Project/project/suba/',
            '/home/test/Project/project/suba/__init__.py',
            '/home/test/Project/project/suba/mod1.py',
            '/home/test/Project/project/subb/',
            '/home/test/Project/project/subb/__init__.py',
            '/home/test/Project/project/subb/mod2.py',
            '/home/test/Project/project/subb/mod3.py',
            ]
        self.sys_modules = {
            'sysmod': 'built-in',
            'testmod': '/usr/lib/python/testmod.py',
            'test2.submod': '/usr/lib/python/test2/submod.py',
            'dll': '/usr/lib/python/dll.so'
        }
        self.submodfile = '/home/test/Project/project/subb/mod2.py'
        self.old_exists = mf.os.path.exists
        self.old_isdir = mf.os.path.isdir
        self.old_find_spec = mf.importlib.util.find_spec
        mf.os.path.exists = self.dummy_exists
        mf.os.path.isdir = self.dummy_isdir
        mf.importlib.util.find_spec = self.dummy_find_spec
        
    def dummy_exists(self, path):
        return path in self.files

    def dummy_isdir(self, path):
        if not path.endswith('/'):
            path = path+'/'
        return path in self.files
        
    def dummy_find_spec(self, path):
        class DummySpec:
            pass
        if path in self.sys_modules:
            spec = DummySpec()
            spec.name = path
            spec.origin = self.sys_modules[path]
            return spec
        else:
            raise ImportError("Could not import {}".format(path))
        
    def tearDown(self):
        mf.os.path.exists = self.old_exists
        mf.os.path.isdir = self.old_isdir
        mf.importlib.util.find_spec = self.old_find_spec
        
    def check_finder(self, path, answer, level=0,
                     from_file = '/home/test/Project/project/main.py', 
                     initial_file = '/home/test/Project/project/main.py'):
        module_path = mf.find_module(path, level, from_file, initial_file)
        self.assertEqual(module_path, answer)
    
    def testSimpleAbsoluteLookup(self):
        self.check_finder('secondary','/home/test/Project/project/secondary.py')
        
    def testFailedAbsoluteLookup(self):
        self.check_finder('tertiary',None)
        
    def testByteCodeLookupFails(self):
        self.check_finder('dll',None)
        
    def testAbsolultePackageLookup(self):
        self.check_finder('suba', '/home/test/Project/project/suba/__init__.py')
        
    def testSubdirAbsoluteLooksup(self):
        self.check_finder('suba.mod1','/home/test/Project/project/suba/mod1.py')
    
    def testSystemModuleLookup(self):
        self.check_finder('testmod', self.sys_modules['testmod'])    
        
    def testSystemSubModuleLookup(self):
        self.check_finder('test2.submod', self.sys_modules['test2.submod'])
        
    def testSystemModuleRelativeLookupFails(self):
        self.check_finder('testmod', None, level=1)
       
    def testBuiltInModuleLookup(self):
        self.check_finder('sysmod', None)
        
    def testSimpleRelativePackageLookup(self):
        self.check_finder(None, '/home/test/Project/project/subb/__init__.py', level=1, from_file=self.submodfile)    
        
    def testSimpleRelativeModuleLookup(self):
        self.check_finder('mod3', '/home/test/Project/project/subb/mod3.py', level=1, from_file=self.submodfile)    
        
    def testParentRelativePackageLookup(self):
        self.check_finder(None, '/home/test/Project/project/__init__.py', level=2, from_file=self.submodfile)    
        
    def testParentRelativeModuleLookup(self):
        self.check_finder('secondary', '/home/test/Project/project/secondary.py', level=2, from_file=self.submodfile)    
        
