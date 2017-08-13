from gi.repository import GObject, Gedit
from .tested.languages.python2 import StatementBlockTypeParser

class TestedPlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "TestedPlugin"
 
    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)
        self.active = False

    def do_activate(self):
        pass

    def do_deactivate(self):
        pass

    def do_update_state(self):
        doc = self.window.get_active_document()
        lang = doc.get_property('language')
        if lang:
            if lang.get_name()=="python":
                self.active = True
                doc.connect("changed",self.doc_changed)
                
    def doc_changed(self, doc):
        parser = StatementBlockTypeParser()
        self.scope = parser.parseStatement(doc.get_property("text"))
        print(self.scope)
