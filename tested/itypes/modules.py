import ast
import sys

from . import basics

class ModuleType(basics.InferredType):
    def __init__(self, name, document, filename):
        self.name = name
        self.document = document
        self.filename = filename

