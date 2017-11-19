import json
import os
import os.path
import webbrowser
import warnings
from gi.repository import GObject, Gedit, Gtk, GtkSource

from .parsers import parse
from .pyweb.module_finder import get_module_dict

warnings.simplefilter('once',UserWarning)

class TestedPlugin(GObject.Object, Gedit.ViewActivatable):
    __gtype_name__ = "TestedPlugin"
 
    view = GObject.property(type=Gedit.View)

    def __init__(self):
        GObject.Object.__init__(self)
        self.active = False
        self.modules_dict = get_module_dict()
        self.context = None

    def do_activate(self):
        self.view.connect("populate-popup",self.add_to_popup)
        self.buffer = self.view.get_buffer()
        self.completion = CompletionProvider(parse)
        completions = self.view.get_completion()
        completions.add_provider(self.completion)
        
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
        
    def update_context(self):
        try:
            self.context = parse.parse_text(self.buffer.get_text())
        except SyntaxError:
            pass
                    
class CompletionProvider(GObject.Object, GtkSource.CompletionProvider):
    def __init__(self, module):
        GObject.Object.__init__(self)
        self.doc_context = None
        self.parser = module.parse_text
        self.suggester = module.get_suggestions
                
    def do_get_name(self):
        return "PyComplete"
        
    def get_icon(self):
        return None
        
    def get_icon_name(self):
        return None
        
    def get_gicon(self):
        return None
        
    def get_all_text(self, iterator):
        buffer = iterator.get_buffer()
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        return buffer.get_text(start, end, True)
        
    def do_populate(self, context):
        pos = context.get_iter()[1]
        location = pos.get_buffer().get_location()
        if location:
            location = location.get_path()
        else:
            location = os.getcwd()
        try:
            self.doc_context = self.parser(self.get_all_text(pos), location)
        except SyntaxError:
            pass
        if self.doc_context:
            line_no = pos.get_line()
            line_start = pos.get_buffer().get_iter_at_line(line_no)
            line = line_start.get_text(pos)
            suggestions = self.suggester(self.doc_context, line, line_no)
            sugs = [self.createProposal(x, info) for x, info in suggestions]
            context.add_proposals(self, sugs, True)
        
    def createProposal(self, text, info):
        prop = GtkSource.CompletionItem(label=text, text=text, info=info)
        return prop
    
    def get_activation(self):
        return 0
        
    def match(self, context):
        return False

