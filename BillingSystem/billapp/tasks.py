from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .models import Bill, BillItem
from decimal import Decimal

@shared_task
def send_invoice_email(bill_id):
    bill = Bill.objects.get(id=bill_id)
    bill_items = BillItem.objects.filter(bill=bill).select_related("product")

    subject = f"Invoice for Bill #{bill.id}"

    message = render_to_string("email_invoice.html", {
        "bill": bill,
        "bill_items": bill_items,
    })

    email = EmailMessage(
        subject,
        message,
        to=[bill.customer.email]
    )

    email.content_subtype = "html"
    email.send()
