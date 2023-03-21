""""""
import unittest
from typing import Any
from xwatc import kampf


class TestKampf(unittest.TestCase):

    def testName(self):
        class MitName:
            def __init__(self, n):
                self.name = n
        at = kampf.Attacke("nA", 1100)
        self.assertEqual(at.text(MitName("Du"), [MitName("Franz")]),
                         ("Du setzt nA gegen Franz ein."))
        self.assertEqual(at.text(MitName("Du"), [MitName("Franz"),
                                                 MitName("Josef")]),
                         ("Du setzt nA gegen Franz und Josef ein."))
        self.assertEqual(at.text(MitName("Leonhard Ernie"), [MitName("Franz"),
                                                 MitName("Du"),
                                                 MitName("Patal Patalapatel")]),
                         ("Leonhard Ernie setzt nA gegen Franz, dich und Patal "
                          "Patalapatel ein."))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
