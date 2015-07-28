# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, an open source suite of business apps
# This module copyright (C) 2015 bloopark systems (<http://bloopark.de>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import base64

from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale


class website_sale(website_sale):

    """override the confirm_order from website_sale."""

    @http.route(['/shop/confirm_order'], methods=['POST'], type='http', auth="public", website=True)
    def confirm_order(self, **post):
        """add to confirm_order the attachment."""
        cr, uid, context = request.cr, request.uid, request.context
        order = request.website.sale_get_order(context=context)
        if not order:
            return request.redirect("/shop")

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        values = self.checkout_values(post)
        values["error"] = self.checkout_form_validate(values["checkout"])
        if values["error"]:
            return request.website.render("website_sale.checkout", values)

        self.checkout_form_save(values["checkout"])
        request.session['sale_last_order_id'] = order.id
        request.website.sale_get_order(update_pricelist=True, context=context)

        error = {}
        if error:
            request.session['bp_checkout_file_upload_error'] = error
            ufile = post.pop('ufile')
            if ufile:
                error['ufile'] = 'reset'
            request.session['bp_checkout_file_upload_default'] = post
            return request.redirect('/shop/checkout')

        env = request.env(user=SUPERUSER_ID)

        if post['ufile']:
            attachment_value = {
                'name': post['ufile'].filename,
                'res_name': post['name'],
                'res_model': 'sale.order',
                'res_id': order.id,
                'datas': base64.encodestring(post['ufile'].read()),
                'datas_fname': post['ufile'].filename,
            }
            env['ir.attachment'].create(attachment_value)

        return request.redirect("/shop/payment")
