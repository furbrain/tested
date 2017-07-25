import os
import os.path
import glob

class PluginBase(object):
    """This is a base class for any plugin type we may want"""
    @classmethod
    def getPlugins(cls):
        """ returns a list of classes of all the plugins of this type"""
        return cls.__subclasses__()
        
        
    
def loadPlugins(dir_name):
    old_dir = os.getcwd()
    os.chdir(dir_name)
    try:
        search_glob = os.path.join(dir_name,"*.py")
        plugin_files = glob.glob(search_glob)
        for f in plugin_files:
            module_name = os.path.basename(f)[:-3]
            __import__(module_name)
    finally:
        os.chdir(old_dir) #always return the current working dir to original state

