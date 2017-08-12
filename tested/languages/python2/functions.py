from inferred_types import InferredType

class FunctionType(InferredType):
    def __init__(self, name, args, returns):
        self.name = name
        self.args = args
        self.returns = returns
        self.type = "f(%s) -> (%s)" % (', '.join(args), returns)
        
    def __str__(self):
        return self.type
