# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Payment Provider: Zarinpal',
    'version': '1.0',
    'category': 'Accounting/Payment Providers',
    'sequence': 351,
    'summary': "Zarinpal payment provider for IRAN.",
    'description': " ",  # Non-empty string to avoid loading the README file.
    'author': 'hooshadoo',
    'website': 'https://www.hooshadoo.com/',
    'depends': ['payment'],
    'data': [
        'views/payment_zarinpal_templates.xml',
        'views/payment_provider_views.xml',
        'data/payment_method_data.xml',
        'data/payment_provider_data.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3'
}
