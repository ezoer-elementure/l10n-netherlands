# Copyright 2018-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.misc import formatLang


class VatStatementIcpLine(models.Model):
    _name = "l10n.nl.vat.statement.icp.line"
    _description = "Intra-Community transactions (ICP) line"
    _order = "partner_id, country_code"

    statement_id = fields.Many2one("l10n.nl.vat.statement", ondelete="cascade")
    partner_id = fields.Many2one(
        "res.partner",
        readonly=True,
        required=True,
    )
    partner_name = fields.Char(related="partner_id.name")
    vat = fields.Char(
        string="VAT",
        readonly=True,
    )
    format_vat = fields.Char(
        compute="_compute_format_vat",
    )
    country_code = fields.Char(
        readonly=True,
    )
    currency_id = fields.Many2one("res.currency", readonly=True)
    currency_name = fields.Char(related="currency_id.name", string="Currency Name")
    amount_products = fields.Monetary(readonly=True)
    format_amount_products = fields.Char(compute="_compute_icp_amount_format")
    amount_services = fields.Monetary(readonly=True)
    format_amount_services = fields.Char(compute="_compute_icp_amount_format")

    @api.depends("vat", "country_code")
    def _compute_format_vat(self):
        for line in self:
            if line.country_code and line.vat:
                line.format_vat = line.vat.lstrip(line.country_code)
            else:
                line.format_vat = line.vat

    @api.depends("amount_products", "amount_services")
    def _compute_icp_amount_format(self):
        for line in self:
            amount_products = formatLang(self.env, line.amount_products, monetary=True)
            amount_services = formatLang(self.env, line.amount_services, monetary=True)
            line.format_amount_products = amount_products
            line.format_amount_services = amount_services

    @api.constrains("country_code")
    def _check_country_code(self):
        country_codes = self.mapped("country_code")
        if self.env.ref("base.nl").code in country_codes:
            raise ValidationError(_("Wrong country code (NL) for ICP report."))
        europe_codes = self.env.ref("base.europe").country_ids.mapped("code")
        for code in country_codes:
            if code not in europe_codes:
                raise ValidationError(
                    _(
                        "Wrong country code (%s) for ICP report. "
                        "Please check your configuration."
                    )
                    % code
                )
