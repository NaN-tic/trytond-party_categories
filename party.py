# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.i18n import gettext
from trytond.exceptions import UserError
from trytond.transaction import Transaction

__all__ = ['Party', 'PartyCategory']

"""
Add to categories the following:
 - New type, view --> Like root but inside of it
 - New checkboxes:
    * Unique --> One one child can be in a product at a time
    * Required --> One of its child must be in the product
    * Accounting --> Category related in accounting, will not appear in the
      Many2Many view, but it will on the Accounting Category field
"""


class Party(metaclass=PoolMeta):
    __name__ = 'party.party'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.categories.domain += [('kind', '!=', 'view')]

    @classmethod
    def validate(cls, vlist):
        super(Party, cls).validate(vlist)
        cls._check_categories(vlist)

    @classmethod
    def _check_categories(cls, parties):
        Category = Pool().get('party.category')

        if not Transaction().context.get('check_categories', True):
            return

        required_categories = Category.search([
                ('required', '=', True),
                ('kind', '=', 'view'),
            ])

        unique_categories_ids = [c.id for c in Category.search([
                ('unique', '=', True),
                ('kind', '=', 'view'),
            ])]

        childs_required = []
        for required in required_categories:
            required_id = required.id
            childs = Category.search([
                    ('parent', 'child_of', [required_id]),
                    ('id', '!=', required_id),
                    ])
            childs_required.append([c.id for c in childs])

        for party in parties:
            if childs_required:
                categories_ids = [c.id for c in party.categories]
                exists = cls.check_if_exist(childs_required, categories_ids)
                if not exists:
                    cat_required = [c.name for c in required_categories]
                    raise UserError(gettext('party_categories.missing_categories',
                        party=party.rec_name,
                        categories=', '.join(cat_required[:3])))

            if unique_categories_ids:
                for unique_category_id in unique_categories_ids:
                    # Check if we have more than one child category for each
                    # unique category
                    childs = Category.search([
                        ('parent', 'child_of', unique_category_id)])
                    if len(set(childs) & set(party.categories)) > 1:
                        raise UserError(
                            gettext('party_categories.repeated_unique',
                            party=party.rec_name))

    @staticmethod
    def check_if_exist(list1, list2):
        for party in list2:
            for required_parent in list1:
                if party in required_parent:
                    list1.remove(required_parent)
        return list1 == []


class PartyCategory(metaclass=PoolMeta):
    __name__ = 'party.category'
    kind = fields.Selection([
        ('other', 'Other'),
        ('view', 'View'),
        ], 'Kind', required=True)
    unique = fields.Boolean('Unique',
        states={
            'invisible': Eval('kind') != 'view',
        })
    required = fields.Boolean('Required',
        states={
            'invisible': Eval('kind') != 'view',
        })

    @staticmethod
    def default_kind():
        return 'other'
