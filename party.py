# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval

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


class Party:
    __metaclass__ = PoolMeta
    __name__ = 'party.party'

    @classmethod
    def __setup__(cls):
        super(Party, cls).__setup__()
        cls._error_messages.update({
                'missing_categories': ('The party "%s" is missing some '
                    'required categories: %s'),
                'repeated_unique': ('The party "%s" has repeated '
                    'categories marked as unique'),
                })

    @classmethod
    def validate(cls, vlist):
        super(Party, cls).validate(vlist)
        cls._check_categories(vlist)

    @classmethod
    def _check_categories(cls, parties):
        Category = Pool().get('party.category')

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
                exisits = cls.check_if_exisit(childs_required, categories_ids)
                if not exisits:
                    cat_required = [c.name for c in required_categories]
                    cls.raise_user_error('missing_categories', (party.rec_name,
                        ', '.join(cat_required[:3])))

            if unique_categories_ids:
                childs = Category.search([
                    ('parent', 'child_of', unique_categories_ids),
                    ('id', 'not in', unique_categories_ids)])

                unique_values = filter(lambda a: a in childs, party.categories)
                # Get all parents to compare them
                parents = [u.parent.id for u in unique_values]

                if len(parents) != len(set(parents)):
                    cls.raise_user_error('repeated_unique', party.rec_name)

    @staticmethod
    def check_if_exisit(list1, list2):
        for party in list2:
            for required_parent in list1:
                if party in required_parent:
                    list1.remove(required_parent)
        return list1 == []


class PartyCategory:
    __metaclass__ = PoolMeta
    __name__ = 'party.category'
    kind = fields.Selection([
        ('other', 'Other'),
        ('view', 'View'),
        ], 'Kind', required=True)
    unique = fields.Boolean('Unique',
        states={
            'invisible': Eval('kind') != 'view',
        }, depends=['kind'])
    required = fields.Boolean('Required',
        states={
            'invisible': Eval('kind') != 'view',
        }, depends=['kind'])

    @staticmethod
    def default_kind():
        return 'other'
