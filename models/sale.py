# -*- coding: utf-8 -*-
from openerp.models import TransientModel
from openerp import fields

class WebsiteConfigSettings(TransientModel):
    _inherit = 'sale.order'

    file = fields.Binary(
         help="This field holds the Files for the Sale Order",
         string='Uploaded Files'
    )
