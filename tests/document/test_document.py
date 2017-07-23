import unittest
import tested.document
import mock

class TestDocument(unittest.TestCase):
    def test_new_with_no_args(self):
        doc = tested.document.Document()

    def test_new_with_single_line_content(self):
        doc = tested.document.Document("Here be content")
        self.assertEqual(doc.lines,["Here be content"])
        
    def test_new_with_multi_line_contenr(self):
        doc = tested.document.Document("Line 1\nLine2")
        self.assertEqual(doc.lines,["Line 1","Line2"])
        
    def test_openFromFilename_with_bad_name(self):
        with self.assertRaises(IOError):
            doc = tested.document.Document.openFromFilename("badname.xrt")
            
    def test_openFromFilename_with_valid_data(self):
        mocked_open = mock.mock_open(read_data="test content")
        with mock.patch("__builtin__.open", mocked_open):
            doc = tested.document.Document.openFromFilename("goodname.py")
            self.assertEqual(doc.lines,["test content"])
