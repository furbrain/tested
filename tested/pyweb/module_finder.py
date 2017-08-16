#standard library module downloader...

import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
import json
import os.path
import os
import re

INDEX_DOC = 'https://docs.python.org/3/py-modindex.html'
LIBRARY_BASE = 'https://docs.python.org/3/'
FNAME = 'module_dict.json'
def download_mod_dict():
    with urllib.request.urlopen(INDEX_DOC) as response:
        source = response.read()
    source = source.replace(b"&copy;", b"")
    root = ET.fromstring(source)
    ns = {'html':'http://www.w3.org/1999/xhtml'}
    entries = root.findall(".//html:code[@class='xref']/..[@href]", ns)
    result = {}
    for entry in entries:
        href = entry.attrib['href']
        text = entry.find('html:code', ns).text
        result[text] = LIBRARY_BASE + href
        
    return result

def get_mod_dict_file():
    return os.path.join(os.path.dirname(__file__), FNAME)

def get_module_dict():
    try:
        with open(get_mod_dict_file(),'r') as f:
            mod_dict = json.load(f)
    except (IOError, json.JSONDecodeError):
        mod_dict = download_mod_dict()
        with open(get_mod_dict_file(),'w') as f:
            json.dump(mod_dict,f)
    return mod_dict
    
if __name__=="__main__":
    os.remove(get_mod_dict_file())
    d = get_module_dict()
    print(d)
