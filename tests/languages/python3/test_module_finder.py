import unittest
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
            ]
        self.old_exists = mf.os.path.exists
        self.old_isdir = mf.os.path.isdir
        mf.os.path.exists = self.dummy_exists
        mf.os.path.isdir = self.dummy_isdir
        
    def dummy_exists(self, path):
        return path in self.files

    def dummy_isdir(self, path):
        if not path.endswith('/'):
            path = path+'/'
        return path in self.files
        
    def tearDown(self):
        mf.os.path.exists = self.old_exists
        mf.os.path.isdir = self.old_isdir
        
    def check_finder(self, path, answer, level=0,
                     from_file = '/home/test/Project/project/main.py', 
                     initial_file = '/home/test/Project/project/main.py'):
        module_path = mf.find_module(path, level, from_file, initial_file)                                  
        self.assertEqual(module_path, answer)
    
    def testSimpleAbsoluteLookup(self):
        self.check_finder('secondary','/home/test/Project/project/secondary.py')
        
    def testFailedAbsoluteLookup(self):
        self.check_finder('tertiary',None)
        
    def testAbsolultePackageLookup(self):
        self.check_finder('suba', '/home/test/Project/project/suba/__init__.py')
        
    def testSubdirAbsoluteLooksup(self):
        self.check_finder('suba.mod1','/home/test/Project/project/suba/mod1.py')
    
        
        
        
