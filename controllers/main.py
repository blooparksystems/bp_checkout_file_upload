# -*- coding: utf-8 -*-
import base64

from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale


import logging
_logger = logging.getLogger(__name__)


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
