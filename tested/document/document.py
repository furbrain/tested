class Document(object):
    def __init__(self, content=""):
        self.lines = content.splitlines()
    
    @classmethod
    def openFromFilename(cls,name):        
        f = open(name,"r")
        return cls(f.read())
        
