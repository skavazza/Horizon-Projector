# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'betorodriuges@msn.com'
__date__ = '2026-01-11'
__copyright__ = 'Copyright 2026, Alberto Rodrigues'

import unittest

from qgis.PyQt.QtGui import QIcon



class horizonDialogTest(unittest.TestCase):
    """Test rerources work."""

    def setUp(self):
        """Runs before each test."""
        pass

    def tearDown(self):
        """Runs after each test."""
        pass

    def test_icon_png(self):
        """Test we can click OK."""
        path = ':/plugins/horizon/icon.png'
        icon = QIcon(path)
        self.assertFalse(icon.isNull())

if __name__ == "__main__":
    suite = unittest.makeSuite(horizonResourcesTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)



