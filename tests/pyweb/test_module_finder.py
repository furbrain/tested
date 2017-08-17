import unittest
import unittest.mock as mock
import tested.pyweb.module_finder as module_finder
import io
import json

HTML_HEADER = b'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'''

def make_html(bytes):
    HEADER = b'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
  <html xmlns="http://www.w3.org/1999/xhtml">'''
    FOOTER = b'</html>'
    return HEADER + bytes + FOOTER

class TestDownload(unittest.TestCase):

    @mock.patch('tested.pyweb.module_finder.urllib.request.urlopen')
    def testCallsCorrectURL(self, mock_urllib):
        mock_urllib.return_value = io.BytesIO(make_html(b''))
        results = module_finder.download_mod_dict()
        self.assertEqual(results,{})
        mock_urllib.assert_called_once_with(module_finder.INDEX_DOC)
        
    @mock.patch('tested.pyweb.module_finder.urllib.request.urlopen')
    def testGetsCorrectData(self, mock_urllib):
        mock_urllib.return_value = io.BytesIO(make_html(b"<a href='x.html'><code class='xref'>XXX</code></a>"))
        results = module_finder.download_mod_dict()
        self.assertEqual(results,{'XXX':module_finder.LIBRARY_BASE+'x.html'})
        
class TestGetModules(unittest.TestCase):
    
    @mock.patch('tested.pyweb.module_finder.get_mod_dict_file')
    def testWithNoPreviousDownload(self, mock_get_file):
        dct = {'testy':'testy.html'}
        with mock.patch('tested.pyweb.module_finder.open',mock.mock_open()) as mock_opener:
            with mock.patch('tested.pyweb.module_finder.download_mod_dict') as downloader:
                downloader.return_value=dct
                mock_get_file.return_value="123.json"
                mock_opener.side_effect=[IOError,io.StringIO()]
                results = module_finder.get_module_dict()
                mock_opener.assert_has_calls([mock.call("123.json","r"),mock.call("123.json","w")])
            
    @mock.patch('tested.pyweb.module_finder.get_mod_dict_file')
    def testWithPreviousDownload(self, mock_get_file):
        with mock.patch('tested.pyweb.module_finder.open',mock.mock_open()) as mock_opener:
            mock_get_file.return_value="123.json"
            dct = {'testy':'testy.html'}
            mock_opener.side_effect=[io.StringIO(json.dumps(dct))]
            results = module_finder.get_module_dict()
            mock_opener.assert_has_calls([mock.call("123.json","r")])   
            self.assertEqual(results, dct)         
