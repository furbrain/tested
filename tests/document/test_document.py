import unittest
import tested.document
import mock

class TestDocument(unittest.TestCase):
    def setUp(self):
        self.content = "Line 1\nLine 2\nLine 3"
        self.content_lines = self.content.splitlines()
        self.fname = "/a random directory/testxyz.py"

    def test_new_with_no_args(self):
        doc = tested.document.Document()

    def test_new_with_single_line_content(self):
        doc = tested.document.Document("Here be content")
        self.assertEqual(doc.lines,["Here be content"])
        
    def test_new_with_multi_line_content(self):
        doc = tested.document.Document(self.content)
        self.assertEqual(doc.lines,self.content_lines)
        
    def test_openFromFilename_with_bad_name(self):
        mocked_open = mock.mock_open()
        mocked_open.side_effect = IOError("bad filename")
        with mock.patch("__builtin__.open", mocked_open):
            with self.assertRaises(IOError):
                doc = tested.document.Document.openFromFilename(self.fname)
            
    def test_openFromFilename_with_valid_data(self):
        mocked_open = mock.mock_open(read_data=self.content)
        with mock.patch("__builtin__.open", mocked_open):
            doc = tested.document.Document.openFromFilename("goodname.py")
            self.assertEqual(doc.lines,self.content_lines)
            
    def test_saveToFilename(self):
        mocked_open = mock.mock_open()
        with mock.patch("__builtin__.open", mocked_open):
            doc = tested.document.Document(self.content)
            doc.saveToFilename(self.fname)
        mocked_open.assert_called_once_with(self.fname,"w")
        file_handle = mocked_open()
        file_handle.write.assert_called_once_with(self.content)
        
