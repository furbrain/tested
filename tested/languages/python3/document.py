from . import modules

class Document:
    def __init__(self, text, location):
        self.text = text
        self.location = location
        self.module = modules.ModuleType.fromText(text, location, self)
        self.module.parseText(text)
        self.scopes = self.module.scope_list





