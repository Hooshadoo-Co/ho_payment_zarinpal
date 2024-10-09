# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint

import requests
from odoo import _, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.ho_payment_zarinpal import const

_logger = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('zarinpal', 'Zarinpal')], ondelete={'zarinpal': 'set default'}
    )
    
    zarinpal_merchant_id = fields.Char(string="Merchant ID", help="The ID solely used to identify the merchant account with Zarinpal", required_if_provider='zarinpal')

    #=== BUSINESS METHODS ===#
        
    def _get_supported_currencies(self):
        """ Override of `payment` to return the supported currencies. """
        supported_currencies = super()._get_supported_currencies()
        if self.code == 'zarinpal':
            supported_currencies = supported_currencies.filtered(
                lambda c: c.name in const.SUPPORTED_CURRENCIES
            )
        return supported_currencies

    def _zarinpal_make_request(self, data=None):
        """ Make a request at Zarinpal endpoint.

        Note: self.ensure_one()

        :param str endpoint: The endpoint to be reached by the request
        :param dict data: The payload of the request
        :param str method: The HTTP method of the request
        :return The JSON-formatted content of the response
        :rtype: dict
        :raise: ValidationError if an HTTP error occurs
        """
        self.ensure_one()
        endpoint = 'https://api.zarinpal.com/pg/v4/payment/request.json'

        try:
            response = requests.post(endpoint, data=data, timeout=60)
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                _logger.exception(
                    "Invalid API request at %s with data:\n%s", endpoint, pprint.pformat(data)
                )
                raise ValidationError(
                    "Zarinpal: " + _(
                        "The communication with the API failed. SEP gave us the following "
                        "information: %s", response.json().get('detail', '')
                    ))
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            _logger.exception("Unable to reach endpoint at %s", endpoint)
            raise ValidationError(
                "Zarinpal: " + _("Could not establish the connection to the API.")
            )
        return response.json()

    def _get_default_payment_method_codes(self):
        """ Override of `payment` to return the default payment method codes. """
        default_codes = super()._get_default_payment_method_codes()
        if self.code != 'zarinpal':
            return default_codes
        return const.DEFAULT_PAYMENT_METHODS_CODES
    
    def _zarinpal_verify_request(self, data):
        """ Make a request at Zarinpal endpoint.

        Note: self.ensure_one()

        :param str endpoint: The endpoint to be reached by the request
        :param dict data: The payload of the request
        :param str method: The HTTP method of the request
        :return The JSON-formatted content of the response
        :rtype: dict
        :raise: ValidationError if an HTTP error occurs
        """
        self.ensure_one()
        endpoint = 'https://api.zarinpal.com/pg/v4/payment/verify.json'

        try:
            response = requests.post(endpoint, data={
                **data,
                'merchant_id': self.zarinpal_merchant_id,
            }, timeout=60)
            
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                _logger.exception(
                    "Invalid API request at %s with data:\n%s", endpoint, pprint.pformat(data)
                )
                raise ValidationError(
                    "Zarinpal: " + _(
                        "The communication with the API failed. SEP gave us the following "
                        "information: %s", response.json().get('detail', '')
                    ))
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            _logger.exception("Unable to reach endpoint at %s", endpoint)
            raise ValidationError(
                "Zarinpal: " + _("Could not establish the connection to the API.")
            )
        return response.json()