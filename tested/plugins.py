import imp
import os.path
import glob

class PluginBase(object):
    """This is a base class for any plugin type we may want"""
    @classmethod
    def getPlugins(cls):
        """ returns a list of classes of all the plugins of this type"""
        return cls.__subclasses__()
        
        
    
def loadPlugins(dir_name):
    search_glob = os.path.join(dir_name,"*.py")
    plugin_files = glob.glob(search_glob)
    for f in plugin_files:
        module_name = "plugins." + os.path.basename(f)[:-3]
        imp.load_source(module_name, f)

