import unittest
import server


class TestServer(unittest.TestCase):

    def test_call_simpler_html2text(self):
        result = server.call_simpler_html2text("<p><br></p><p><a href=\"https://www.bbc.com/\" rel=\"noopener noreferrer\" target=\"_blank\">sadsad</a></p><p>Very interesting article</p><ol><li><strong>bo</strong>ld and list option 1</li></ol><p><strong><em>italic bold text </em></strong></p><ul><li><br></li><li>option 1</li><li>option 2</li><li>option 3</li><li>sadfadsf</li></ul><p><br></p><p><br></p><p><br></p><p><br></p><p><br></p><p><br></p><h1>Header very huge</h1>")
        self.assertEqual(result, 'sadsad\nVery interesting article\n1. bold and list option 1\nitalic bold text\noption 1\noption 2\noption 3\nsadfadsf\nHeader very huge')
        result = server.call_simpler_html2text("Hello my <b>nam</b>e is <b>Bold. </b><i>I'm 20 years old.</i><div><ol><li>One</li><li>Two</li><li>Three</li></ol><ul><li>I'm a bullet</li></ul>I´m a link <a href=\"http://www.smarp.com\" title=\"\">www.smarp.com</a></div><div><br></div><div>I´m <u>underlined</u></div><div><strike>Strike me through</strike></div><div><strike><br></strike></div><h1>H1</h1><div><br></div><h2>H2</h2><h3>H3</h3><div><br></div><div><i>I'm Italic</i></div>")
        self.assertEqual(result, "Hello my name is Bold. I'm 20 years old.\n1. One\n2. Two\n3. Three\nI'm a bullet\nI´m a link www.smarp.com\nI´m underlined\nStrike me through\nH1\nH2\nH3\nI'm Italic")
        result = server.call_simpler_html2text("I´m")
        self.assertEqual(result, 'I´m')
        result = server.call_simpler_html2text("<ol><li>number one </li><li>number two</li><li>number three</li></ol><p><br></p><p>Test article</p><h2>Header average</h2><p><br></p><p><strong>Very interesting my one at on article</strong></p><ol><li><strong>first bold and list option </strong></li></ol><p><strong><em>italic bold text </em></strong></p><ul><li>option 0</li><li>option 1</li><li>option 2</li></ul><p><br></p><p><br></p><p><br></p><p><br></p><p><br></p><p><br></p><p><br></p><p><br></p><p><br></p><p><br></p><p><br></p><p><br></p><p><br></p><p><br></p><p><br></p><p><br></p><p><br></p><p><br></p><p><br></p><h1>Header very huge</h1>")
        self.assertEqual(result, "1. number one \n2. number two\n3. number three\nTest article\nHeader average\nVery interesting my one at on article\n1. first bold and list option \nitalic bold text\noption 0\noption 1\noption 2\nHeader very huge")
