# Billing and Invoices

**Summary:**
A complete guide to understanding your TeamFlow billing cycle, accessing invoices, updating payment methods, and resolving common billing issues.

**Tags:** billing, invoices, payment, credit card, receipts, charges, refund, billing cycle, finance

---

## Overview

TeamFlow bills customers on either a **monthly** or **annual** cycle, depending on the plan selected at signup. All charges are processed in USD and invoices are generated automatically at the start of each billing period.

---

## Accessing Your Invoices

1. Log in to your TeamFlow workspace as an **Admin** or **Billing Manager**.
2. Navigate to **Settings → Billing → Invoice History**.
3. All invoices are listed with their status: `Paid`, `Unpaid`, or `Void`.
4. Click **Download PDF** next to any invoice to save a copy for your records.

> Invoices are also automatically emailed to the billing contact address on file after each successful charge.

---

## Understanding Invoice Statuses

| Status   | Meaning                                                                 |
|----------|-------------------------------------------------------------------------|
| `Paid`   | Payment was collected successfully.                                     |
| `Unpaid` | Payment is due or has failed. Action required.                          |
| `Void`   | Invoice was cancelled (e.g., after a plan change mid-cycle).            |
| `Past Due` | Payment has not been received by the due date. Service may be affected. |

---

## Updating Your Payment Method

1. Go to **Settings → Billing → Payment Methods**.
2. Click **Add Payment Method** and enter your new card details.
3. Set the new card as **Default** and remove the old one if desired.

> TeamFlow accepts all major credit and debit cards (Visa, Mastercard, American Express, Discover). We do not store raw card data — all payments are processed securely via Stripe.

---

## Failed Payments

If a payment fails, TeamFlow will:

1. Retry the charge automatically after **3 days**.
2. Send an email notification to the billing contact.
3. Retry again after **7 days** if the second attempt fails.
4. Mark the subscription as **Past Due** and restrict access to premium features after **14 days** of non-payment.

To resolve a failed payment, update your payment method (see above) and click **Retry Payment** in **Settings → Billing**.

---

## Requesting a Refund

TeamFlow offers a **7-day refund window** for annual plan purchases. To request a refund:

- Contact support at **support@teamflow.io** within 7 days of the charge.
- Include your company name, invoice number, and reason for the request.

Monthly plan charges are non-refundable but you can cancel at any time to stop future billing.

---

## Billing for Seat Changes

If you add users mid-billing-cycle, you will be charged a **prorated amount** for the remaining days in the period. Removals take effect at the end of the current billing period — no credit is issued for partial months.

---

## FAQs

**Q: Can I get an invoice with our company's VAT number?**
Yes. Go to **Settings → Billing → Tax Information** and enter your VAT/tax ID. It will appear on all future invoices.

**Q: Why does my invoice show a different amount than expected?**
This may be due to proration from a mid-cycle plan change or seat addition. Contact support if the amount is still unclear.

**Q: Can I switch from monthly to annual billing?**
Yes. Go to **Settings → Billing → Change Plan** and select **Annual**. The switch takes effect at the start of your next billing cycle.
