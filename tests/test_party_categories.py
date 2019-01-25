# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import test_view, test_depends


class TestPartyCategoriesCase(unittest.TestCase):
    'Test Party Categories module'

    def setUp(self):
        trytond.tests.test_tryton.install_module('party_categories')

    def test0005views(self):
        'Test views'
        test_view('party_categories')

    def test0006depends(self):
        'Test depends'
        test_depends()


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            TestPartyCategoriesCase))
    return suite
