import unittest
import tested.document

class TestDocument(unittest.TestCase):
    def test_newDocumentWorks(self):
        doc = tested.document.Document()
        
    def test_openDocument_with_bad_name(self):
        with self.assertRaises(IOError):
            doc = tested.document.Document.openFromFile("badname.xrt")
