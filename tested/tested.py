import json
import os.path
import webbrowser
from gi.repository import GObject, Gedit, Gtk

from .languages.python3 import StatementBlockTypeParser
from .pyweb.module_finder import get_module_dict

class TestedPlugin(GObject.Object, Gedit.ViewActivatable):
    __gtype_name__ = "TestedPlugin"
 
    view = GObject.property(type=Gedit.View)

    def __init__(self):
        GObject.Object.__init__(self)
        self.active = False
        self.modules_dict = get_module_dict()

    def do_activate(self):
        self.view.connect("populate-popup",self.add_to_popup)

    def do_deactivate(self):
        pass

    def do_update_state(self):
        pass
                
    def add_to_popup(self, view, popup):
        #get pointer coords
        pos = self.get_pointer_position(view)
        buffer_iter = view.get_iter_at_location(pos.buffer_x, pos.buffer_y)
        text = self.get_word_from_iter(buffer_iter.iter)
        if text in self.modules_dict:
            func = lambda: self.browser_open(self.modules_dict[text])
            menu_item = self.make_menu_item("Pydocs for {}".format(text), func)
            popup.append(menu_item)
        return True

    def get_pointer_position(self, view):
        gdkwin = view.get_window(Gtk.TextWindowType.WIDGET)
        display = gdkwin.get_display()
        seat = display.get_default_seat()
        pointer = seat.get_pointer()
        pos = gdkwin.get_device_position(pointer)
        pos = view.window_to_buffer_coords(Gtk.TextWindowType.WIDGET, pos.x, pos.y)
        return pos
        
    def get_word_from_iter(self, text_iter):
        text_start = text_iter.copy()
        text_start.backward_word_start()
        text_end = text_start.copy()
        text_end.forward_word_end()
        text = text_start.get_text(text_end)
        return text
        
    def make_menu_item(self, label, action):
        menu_item = Gtk.MenuItem()
        menu_item.set_label(label)
        menu_item.show()
        menu_item.connect("activate",lambda x: action())
        return menu_item
        
    def browser_open(self, url):
        print("Opening {}".format(url))
        webbrowser.open(url, new=2)
        
