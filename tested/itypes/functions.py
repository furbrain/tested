import ast

from . import basics, builtins
from .. import utils

class FunctionType(basics.InferredType):
    def __init__(self, name, args, returns, docstring):
        super().__init__()
        self.name = name
        self.args = args
        self.return_values = returns
        self.type = "FUNCTION"
        self.docstring = docstring

    @utils.do_not_recurse('...')
    def __str__(self):
        return "%s(%s) -> (%s)" % (self.name, ', '.join(self.args), self.return_values)

    def get_call_return(self, arg_types):
        return_typeSet = basics.TypeSet()
        type_mapping = {k: v for k, v in zip(self.args, arg_types)}
        for possible_type in self.return_values:
            if isinstance(possible_type, basics.UnknownType):
                replacement_type = type_mapping.get(possible_type.type, basics.UnknownType())
                return_typeSet = return_typeSet.add_type(replacement_type)
            else:
                return_typeSet = return_typeSet.add_type(possible_type)
        return return_typeSet
