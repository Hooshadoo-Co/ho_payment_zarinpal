# Zarinpal

## Technical details

Documentation: [Payments API](https://www.zarinpal.com/docs/paymentGateway/)

This module integrates Zarinpal using tokenization and form
submission provided by the `payment` module.

## Supported features
- Tokenization with payment
- Payment with redirection flow

## Not implemented features
- Webhook notifications

## Configuration
1. Go to the **Website menu** in the site management section.
2. Select the **Payment Providers** option from the **Configuration menu** and **eCommerce section**.
3. Open **Zarinpal** provider.
4. Change the **state** of the payment provider to **Enabled**.
5. In the **Credentials tab**, set the following fields based on the information provided by Zarinpal.
    - zarinpal_merchant_id: Zarinpan Merchant ID
6. In the **Configuration tab**, then the **Payment Form section** and then the **Payment Methods**, select **Enable Payment Methods link** and activate the **Zarinpal payment method** on the opened page.
7. Publish it for display on the website.