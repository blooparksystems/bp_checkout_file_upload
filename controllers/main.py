# -*- coding: utf-8 -*-
import base64

from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request

import logging
_logger = logging.getLogger(__name__)

class checkout_file_upload(http.Controller):

    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True)
    def confirm_order(self, **post):
        logging.warning('post /shop/confirm_order')
        logging.warning(post)
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry

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

        logging.warning('order number')
        logging.warning(order)
        env = request.env(user=SUPERUSER_ID)
        if post['ufile']:
            logging.warning('found attachment in post')
            attachment_value = {
                'name': post['ufile'],
                'res_name': post['name'],
                'res_model': 'sale.order',
                'res_id': order,
                'datas': base64.encodestring(post['ufile']),
                'datas_fname': post['ufile'],
            }
            logging.warning('value update')
            logging.warning(attachment_value)
            logging.warning('create attachment')
            env['ir.attachment'].create(attachment_value)

        return request.redirect("/shop/payment")