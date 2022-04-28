
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.exceptions import UserError


class PartyCategoriesTestCase(ModuleTestCase):
    'Test PartyCategories module'
    module = 'party_categories'

    @with_transaction()
    def test_check_categories(self):
        pool = Pool()
        Party = pool.get('party.party')
        Category = pool.get('party.category')

        category_required = Category()
        category_required.name = 'Category Required'
        category_required.required = True
        category_required.kind = 'view'
        category_required.save()

        category = Category()
        category.name = 'Category'
        category.save()

        party = Party()
        party.name = 'Party'
        party.categories = [category]

        self.assertRaises(UserError, Party.create,
            [party._save_values])

    @with_transaction(context={'check_categories': False})
    def test_not_check_categories(self):
        pool = Pool()
        Party = pool.get('party.party')
        Category = pool.get('party.category')

        category_required = Category()
        category_required.name = 'Category Required'
        category_required.required = True
        category_required.kind = 'view'
        category_required.save()

        category = Category()
        category.name = 'Category'
        category.save()

        party = Party()
        party.name = 'Party'
        party.categories = [category]
        party.save()
        self.assertTrue(party.id)


del ModuleTestCase
