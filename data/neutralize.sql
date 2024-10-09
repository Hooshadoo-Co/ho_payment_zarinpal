-- disable zarinpal payment provider
UPDATE payment_provider
   SET zarinpal_merchant_id = NULL;
