from ..plugins import PluginBase
import ast

class PythonPlugin(PluginBase):
    def parseText(self, text):
        """Parse a python source file, generate a list of identifiers (classes, functions, variables)
           and possible completions for each of these"""
        self.parse_tree = ast.parse(text)
        
      


