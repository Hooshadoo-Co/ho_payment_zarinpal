# Part of Odoo. See LICENSE file for full copyright and licensing details.
SUPPORTED_LOCALES = [
    'fa_IR',
]

# Currency codes in ISO 4217 format supported by mollie.
# Note: support varies per payment method.
SUPPORTED_CURRENCIES = [
    # 'IRR',
]

# The codes of the payment methods to activate when Zarinpal is activated.
DEFAULT_PAYMENT_METHODS_CODES = [
    # Primary payment methods.
    'zarinpal',
]

# Mapping of payment method codes to Zarinpal codes.
PAYMENT_METHODS_MAPPING = {
    'zarinpal': 'zarinpal',
}
