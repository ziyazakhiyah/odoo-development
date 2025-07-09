# -*- coding: utf-8 -*-
import hmac, hashlib, json, requests
import uuid
from datetime import datetime, timezone
from math import floor
from odoo import fields, models


class Crypto:
    """To calculate the hmac of the params then hash with sha256 algorithm"""

    @staticmethod
    def compute_sha256_hash(message: str, secret: str) -> str:
        """To hash hmac and secret key with sha256 algorithm"""
        hash_key = hmac.new(secret.encode(), message.encode() ,digestmod=hashlib.sha256)
        return hash_key.hexdigest()

    def calculate_hmac(self, secret: str, header_params: dict, body: str='') -> str:
        """To compute hmac"""
        data = []
        for key,value in header_params.items():
              if key.startswith('checkout-'):
                data.append('{key}:{value}'.format(key = key, value = value))
        data.append(body)
        return self.compute_sha256_hash('\n'.join(data), secret)

class PaymentProvider(models.Model):
    """Adding required fields for Paytrail Integration"""
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('paytrail', "Paytrail")], ondelete={'paytrail': 'set default'}
    )
    paytrail_merchant_id = fields.Char(
        string="Paytrail Merchant ID",
        help="The key solely used to identify the account with Paytrail.",
        required_if_provider='paytrail',
    )
    paytrail_secret_key = fields.Char(
        string="Paytrail Key Secret",
        required_if_provider='paytrail',
        groups='base.group_system',
    )

    def paytrail_create_payment(self, transaction):
        """Initializing payload and headers then creating payment request"""
        from_currency = transaction.currency_id
        to_currency = self.env['res.currency'].search([('name', '=', 'EUR')], limit=1)
        converted_amount = from_currency._convert(transaction.amount, to_currency, self.env.company, datetime.now()) * 100
        if from_currency != to_currency:
            converted_amount = floor(converted_amount)
        payload = {
            "stamp": str(uuid.uuid4()),
            "reference": transaction.reference,
            "amount": converted_amount,
            "currency": "EUR",
            "language": "EN",
            "items": [{
                "unitPrice": converted_amount,
                "units": 1,
                "vatPercentage": 15,
                "productCode": transaction.reference,
                "stamp": str(uuid.uuid4())
            }],
            "customer": {"email": transaction.partner_email},
            "redirectUrls": {
                "success": transaction.provider_id.get_base_url() + "/payment/paytrail/success",
                "cancel": transaction.provider_id.get_base_url() + "/payment/paytrail/cancel",
            },
        }
        headers = {
            "checkout-account": self.paytrail_merchant_id,
            "checkout-algorithm": "sha256",
            "checkout-method": "POST",
            "checkout-nonce": str(uuid.uuid4()),
            "checkout-timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "Z",
            "content-type": "application/json"
        }
        body = json.dumps(payload, separators=(',', ':'))
        enc_data = Crypto.calculate_hmac(Crypto, self.paytrail_secret_key, headers, body)
        headers["signature"] = enc_data
        response = requests.post("https://services.paytrail.com/payments", headers=headers, data=body)
        if response.status_code == 201:
            return response.json()["href"]
        else:
            raise Exception(f"Paytrail Error: {response.text}")
