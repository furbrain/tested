import os.path

def find_module(path, level, from_file, initial_file):
    initial_dir = os.path.dirname(initial_file)
    path = os.path.join(*path.split('.'))
    possible_path = os.path.join(initial_dir,path)
    if os.path.isdir(possible_path):
        possible_path = os.path.join(possible_path,'__init__')
    possible_path += '.py'
    if os.path.exists(possible_path):
        return possible_path
    else:
        return None
