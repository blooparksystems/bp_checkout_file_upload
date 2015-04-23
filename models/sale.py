# -*- coding: utf-8 -*-
from openerp.models import TransientModel
from openerp.models import Model
from openerp import fields

import logging
_logger = logging.getLogger(__name__)

class sale_order(TransientModel):
    _inherit = 'sale.order'

    file = fields.One2many('ir.attachment', 'partner_id', string="Attachments")

class document_file(Model):
    _inherit = 'ir.attachment'

    def create(self, cr, uid, vals, context=None):
        if vals.get('partner_id', 0) != 0 and not (vals.get('res_id', False) and vals.get('res_model', False)):
            vals['res_id'] = vals['partner_id']
            vals['res_model'] = 'res.partner'
        return super(document_file, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('partner_id', 0) != 0 and not (vals.get('res_id', False) and vals.get('res_model', False)):
            vals['res_id'] = vals['partner_id']
            vals['res_model'] = 'res.partner'
        return super(document_file, self).write(cr, uid, ids, vals, context)

