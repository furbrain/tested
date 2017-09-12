import os.path
import importlib.util


def find_module(path, level, from_file, initial_file):
    possible_path = get_possible_path(path, initial_file)
    if os.path.isdir(possible_path):
        possible_path = os.path.join(possible_path,'__init__')
    possible_path += '.py'
    if os.path.exists(possible_path):
        return possible_path
    else:
        if level==0:
            return get_builtin_module(path)
    return None
    
def get_possible_path(path, starting_file, levels=0):
    starting_dir = os.path.dirname(starting_file)
    file_path = os.path.join(*path.split('.'))
    possible_path = os.path.join(starting_dir,file_path)
    return possible_path
    
def get_builtin_module(path):
    spec = importlib.util.find_spec(path)
    if spec:
        if spec.origin == "built-in":
            return None
        else:
            return spec.origin
    else:
        return None