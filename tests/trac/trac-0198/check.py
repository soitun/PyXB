# -*- coding: utf-8 -*-
import logging
if __name__ == '__main__':
    logging.basicConfig()
_log = logging.getLogger(__name__)
import unittest

import wsse
import wsu

from pyxb_123.utils.domutils import BindingDOMSupport

BindingDOMSupport.DeclareNamespace(wsu.Namespace, 'wsu')
BindingDOMSupport.DeclareNamespace(wsse.Namespace, 'wsse')

class TestTrac0198 (unittest.TestCase):
    def testFindWsu (self):
        self.assertEqual(3, len(wsse.tAttributedString._AttributeMap))
        for (n, ad) in wsse.tAttributedString._AttributeMap.iteritems():
            if (n.localName() == "agu"):
                self.assertEqual(None, n.namespace())
            else:
                self.assertEqual(wsu.Namespace, n.namespace())
        self.assertEqual(2, len(wsse.tComplexElt._ElementMap))
        for (n, ad) in wsse.tComplexElt._ElementMap.iteritems():
            if n.localName() == 'Elt':
                self.assertEqual(wsu.Namespace, n.namespace())
            elif n.localName() == 'local':
                self.assertEqual(None, n.namespace())
            else:
                self.assertFalse()

if __name__ == '__main__':
    unittest.main()
