import unittest
import tested.plugins
import os

class TestPlugins(unittest.TestCase):
    def setUp(self):
        self.fixtureDir = os.path.join(os.path.dirname(__file__),"fixtures")

    def testInitWorks(self):
        tested.plugins.loadPlugins(self.fixtureDir)
        
    def testInitLoadsRelevantPlugins(self):
        tested.plugins.loadPlugins(self.fixtureDir)
        plugin_names = set([x.__name__ for x in tested.plugins.PluginBase.getPlugins()])
        self.assertEqual(set(["PythonPlugin", "RubyPlugin"]), plugin_names)
        
    def testInitPreservesCurrentWorkingDirectory(self):
        old_dir = os.getcwd()
        tested.plugins.loadPlugins(self.fixtureDir)
        new_dir = os.getcwd()
        self.assertEqual(old_dir,new_dir)        
