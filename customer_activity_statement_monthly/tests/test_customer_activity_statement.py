# Copyright 2018 Graeme Gellatly.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta
from odoo.tests.common import TransactionCase


class TestCustomerActivityStatement(TransactionCase):
    """
    Tests for Customer Activity Statement.
    """

    def setUp(self):
        super().setUp()
        self.day_report = self.env[
            "report.customer_activity_statement.statement"
        ].with_context(aging_type="days")
        self.month_report = self.env[
            "report.customer_activity_statement.statement"
        ].with_context(aging_type="months")
        self.today = datetime.today().date()
        partner_id = self.env.ref("base.res_partner_1").id
        self.partner_ids = [partner_id, self.env.ref("base.res_partner_2").id]
        self.wiz = self.env["customer.activity.statement.wizard"].with_context(
            model="res.partner", active_id=partner_id, active_ids=[partner_id]
        )

    def test_prepare_activity_statement(self):

        stmt = self.wiz.create({})
        self.assertEquals(stmt.aging_type, "months")
        data = stmt._prepare_activity_statement()
        self.assertEquals(data["aging_type"], "months")

    def test_report_dates(self):
        d = self.today.replace(day=1) - timedelta(days=1)
        month_dates = self.month_report._get_bucket_dates(d)
        day_dates = self.day_report._get_bucket_dates(d)

        deltas = []
        for k in ("minus_30", "minus_60", "minus_90", "minus_120"):
            deltas.append((d - month_dates[k]).days)
            d = month_dates[k]
        # Fairly simple validation - in any 4 month period at least 1 month
        # will have 31 days
        self.assertIn(31, deltas)
        self.assertTrue(len(set(deltas)) > 1)
        self.assertNotEquals(month_dates, day_dates)

    def test_get_report_values(self):
        report = self.env["report.customer_activity_statement.statement"]
        # This test and code could be improved by separating out the filters
        # into separate functions, but at least we check the function runs
        data = report.get_report_values(self.partner_ids, None)
        self.assertEquals(data["aging_type"], "months")
