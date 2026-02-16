from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import render, redirect
from billapp.models import Product, Denomination, Bill, BillItem, Customer
from django.db.models import F
from billapp.tasks import send_invoice_email

# Create your views here.

def home(request):
    # Page 1: show drawer denominations (bill is NULL)
    drawer_denoms = Denomination.objects.filter(bill__isnull=True).order_by("-value")
    products = Product.objects.all()
    if request.method == "POST":
        customer_email = request.POST.get("customer_email")
        paid_amount = Decimal(request.POST.get("paid_amount") or "0")
        product_ids = request.POST.getlist("product_id")
        quantities = request.POST.getlist("quantity")
        # print(product_ids, quantity)
        # print("--------------------------------------")
        customer, _ = Customer.objects.get_or_create(email=customer_email)
        bill = Bill.objects.create(customer=customer, paid_amount=paid_amount)
            
        grant_total = Decimal("0.00")
        for product_id, qty_str in zip(product_ids, quantities):
            qty = int(qty_str)
            product = Product.objects.get(id=int(product_id))
            product.available_stocks -= qty
            product.save()
            sub_total = product.price * qty
            total = sub_total + (sub_total * product.tax_percentage / Decimal("100"))
            grant_total += total
            
            BillItem.objects.create(
                product=product,
                quantity=qty,
                price=sub_total,  # unit price
                total=total,
                bill=bill,
            )
        
        bill.total = grant_total
        bill.save()
        return redirect("generate_bill", bill_id = bill.id)
    
    return render(request, "main_bill.html", {"drawer_denoms": drawer_denoms, "products": list(products)})



def generate_bill(request, bill_id):
    send_invoice_email.delay(bill_id)
    bill = Bill.objects.get(id=bill_id)
    bill_items = BillItem.objects.filter(bill=bill).select_related("product")
    total_without_tax = sum(item.price for item in bill_items)
    total_tax = sum(data.price * data.product.tax_percentage / 100 for data in bill_items)
    net_total = sum(item.total for item in bill_items)
    rounded_net_total = net_total.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
     
    bill_balance = abs(bill.balance).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    balance = bill_balance
    result = {}
    denominations = Denomination.objects.filter(bill__isnull=True).values_list("value", flat=True)
    print(balance)
    for val in denominations:
        count = int(balance // val)
        # print(count)
        if count > 0:
            # denominations.filter(value=val).update(count=F('count') - count)
            Denomination.objects.filter(value=val, bill__isnull=True).update(count=F('count') - count)
            result[val] = count
            balance = (balance - (count * val)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    print(result)
    context = {
        "bill": bill,
        "bill_items": bill_items,
        "total_without_tax": total_without_tax,
        "total_tax": total_tax,
        "net_total": net_total,
        "rounded_net_total": rounded_net_total,
        "balance": bill_balance,
        "change_breakdown": result,
    }
    return render(request, "bill_result.html", context = context)

def purchase_history(request):
    customer_email = request.GET.get("email")

    if not customer_email:
        return redirect("home")

    try:
        customer = Customer.objects.get(email=customer_email)
    except Customer.DoesNotExist:
        return render(request, "purchase_history.html", {
            "error": "Customer not found."
        })

    bills = Bill.objects.filter(customer=customer).order_by("-created_at")

    return render(request, "purchase_history.html", {
        "bills": bills,
        "customer": customer
    })
