class Document(object):
    def __init__(self, content=""):
        self.lines = content.splitlines()
    
    @classmethod
    def openFromFilename(cls,filename):
        with open(filename,"r") as f:        
            return cls(f.read())
        
    def saveToFilename(self, filename):
        with open(filename,"w") as f:
            f.write("\n".join(self.lines))
            
        
