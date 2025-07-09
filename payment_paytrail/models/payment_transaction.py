# -*- coding: utf-8 -*-
from odoo import models


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        """Override the default method executed when the Pay Now button"""
        if self.provider_code == 'paytrail':
            redirect_url = f"/payment/paytrail/redirect/{self.id}"
            return {'api_url': redirect_url}
        return super()._get_specific_rendering_values(processing_values)
