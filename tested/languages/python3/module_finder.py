import os.path
import importlib.util

def find_module(path, level, from_file, initial_file):
    initial_dir = os.path.dirname(initial_file)
    file_path = os.path.join(*path.split('.'))
    possible_path = os.path.join(initial_dir,file_path)
    if os.path.isdir(possible_path):
        possible_path = os.path.join(possible_path,'__init__')
    possible_path += '.py'
    if os.path.exists(possible_path):
        return possible_path
    else:
        if level==0:
            spec = importlib.util.find_spec(path)
            if spec:
                return spec.origin
    return None
