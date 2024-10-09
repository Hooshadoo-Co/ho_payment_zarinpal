# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class ZarinpalController(http.Controller):
    _authority_url = '/payment/zarinpal/authority'
    _callback_url = '/payment/zarinpal/callback'

    @http.route(
        _authority_url, type='http', auth='public', methods=['POST'], csrf=False,
        save_session=False
    )
    def zarinpal_authority(self, **data):
        provider_id = int(data.pop('provider_id'))
        provider_sudo = request.env['payment.provider'].sudo().browse(provider_id)
        
        data['amount']=int(data['amount'])

        response = provider_sudo._zarinpal_make_request(data)
        response_data = response.get('data')
        code = response_data.get('code')
        authority = response_data.get('authority')

        _logger.info("Received Zarinpal return authority:\n%s", pprint.pformat(authority))

        if(code and authority):
            tx = request.env['payment.transaction'].sudo().search([('reference', '=', data.get('order_id'))])
            tx.zarinpal_authority = authority
            return request.redirect('https://www.zarinpal.com/pg/StartPay/%s' %authority, code=301, local=False)

        return request.redirect('/shop/payment')

    @http.route(
        _callback_url, type='http', auth='public', methods=['GET'], csrf=False,
        save_session=False
    )
    def zarinpal_return_from_checkout(self, **data):
        """ Process the notification data sent by Zarinpal after redirection from checkout.

        The route is flagged with `save_session=False` to prevent Odoo from assigning a new session
        to the user if they are redirected to this route with a POST request. Indeed, as the session
        cookie is created without a `SameSite` attribute, some browsers that don't implement the
        recommended default `SameSite=Lax` behavior will not include the cookie in the redirection
        request from the payment provider to Odoo. As the redirection to the '/payment/status' page
        will satisfy any specification of the `SameSite` attribute, the session of the user will be
        retrieved and with it the transaction which will be immediately post-processed.

        :param dict data: The notification data (only `id`) and the transaction reference (`ref`)
                          embedded in the return URL
        """
        _logger.info("handling redirection from Zarinpal with data:\n%s", pprint.pformat(data))
        request.env['payment.transaction'].sudo()._handle_notification_data('zarinpal', data)
        return request.redirect('/payment/status')