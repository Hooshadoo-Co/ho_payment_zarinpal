# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from werkzeug import urls

from odoo import _, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.ho_payment_zarinpal.controllers.main import ZarinpalController


_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    zarinpal_authority = fields.Char(string='Zarinpal Authority', readonly=True,help='Reference of the TX as stored in the acquirer database')

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return Zarinpal-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of provider-specific rendering values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'zarinpal':
            return res

        payload = self._zarinpal_prepare_payment_request_payload()
        return payload
    
    def _zarinpal_prepare_payment_request_payload(self):
        """ Create the payload for the payment request based on the transaction values.

        :return: The request payload
        :rtype: dict
        """
        base_url = self.provider_id.get_base_url()
        return {
            'provider_id':self.provider_id.id,
            'merchant_id': self.provider_id.zarinpal_merchant_id,
            'amount': int(self.amount),
            'description': self.partner_name,
            'callback_url': urls.url_join(base_url, ZarinpalController._callback_url),
            'api_url': urls.url_join(base_url, ZarinpalController._authority_url),
            'order_id': self.reference,
        }

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of payment to find the transaction based on Zarinpal data.

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'zarinpal' or len(tx) == 1:
            return tx

        tx = self.search(
            [('zarinpal_authority', '=', notification_data.get('Authority')), ('provider_code', '=', 'zarinpal')]
        )

        if not tx:
            raise ValidationError("Zarinpal: " + _(
                "No transaction found matching reference %s.", tx.reference
            ))
        return tx

    def _process_notification_data(self, notification_data):
        """ Override of payment to process the transaction based on Zarinpal data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider
        :return: None
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'zarinpal':
            return
        
        status = notification_data.get('Status')
        authority = notification_data.get('Authority')

        transaction = self.search([('zarinpal_authority', '=', authority), ('provider_code', '=', 'zarinpal')])
        
        if status == 'OK':
            transaction_result = self.provider_id._zarinpal_verify_request({'authority':authority, 'amount':int(transaction.amount)})

            transaction_result_data = transaction_result.get('data')
            code = transaction_result_data.get('code')
            ref_id = transaction_result_data.get('ref_id')

            if code == 100:
                transaction.provider_reference = ref_id
                self._set_done()
            elif code == 101:
                self._set_done()
            else:
                self._set_error(
                    "Zarinpal: " + _("The payment encountered an error with code %s", code)
                )
        elif status == 'NOK':
            self._set_error(
                "Zarinpal: " + _("The payment encountered an error with code %s", status)
            )
        else : 
            self._set_error(
                "Zarinpal: " + _("The payment encountered an error with code %s", 'Unknown Error')
            )