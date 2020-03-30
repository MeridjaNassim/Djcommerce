from django.shortcuts import render
from .models import Item, OrderItem , Order, BillingAdress, Payment
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, View, DetailView
from .forms import CheckoutForm
import stripe
stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"
# Create your views here.


class HomeView(ListView):
    model = Item
    paginate_by = 6
    template_name  = 'home-page.html'

class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"

@login_required
def add_to_cart(request , slug ):
    item = get_object_or_404(Item , slug = slug)
    orderItem , created = OrderItem.objects.get_or_create(item = item , ordered = False, user = request.user)
    order_qs = Order.objects.filter(user = request.user , ordered =False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug = slug).exists() :
            orderItem.quantity += 1
            orderItem.save()
        else:
            order.items.add(orderItem)
    else:
        order = Order.objects.create(user = request.user)
        messages.info(request  , "A new Order have been created")
        order.items.add(orderItem)
    messages.success(request , "Item added successfuly ")
    return redirect("core:item", slug = slug)

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item , slug = slug)
    order_qs = Order.objects.filter(user = request.user , ordered =False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug = slug ).exists():
            orderItem = OrderItem.objects.get(
            user = request.user ,
            ordered = False,
            item = item
            )
            orderItem.delete()
            messages.success(request , "Product removed from Cart ")
            return redirect("core:item", slug = slug)
        else:
            messages.error( request ,"You havn't purcahsed any product like this ")
            return redirect("core:item", slug = slug)
    else:
        messages.error( request ,"You dont have an active order")
        return redirect("core:item", slug = slug)


class CheckoutView(LoginRequiredMixin,View):
    def get(self, *args , **kwargs):
        context={
            'form':CheckoutForm()
        }
        return render(self.request , 'checkout-page.html', context )
    def post(self , *args , **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order =Order.objects.get( user = self.request.user , ordered = False)
            if form.is_valid():
                street_adress =form.cleaned_data.get('street_adress')
                appartement_adress = form.cleaned_data.get('appartement_adress')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                same_shipping_adress = form.cleaned_data.get('same_shipping_adress')
                save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('pament_option')
                billing_adress = BillingAdress(
                    user = self.request.user ,
                    street_adress = street_adress,
                    appartement_adress = appartement_adress,
                    countries = country,
                    zip = zip
                )
                billing_adress.save()
                return redirect('core:checkout')
            else:
                messages.error(self.request , "Invalid Input ")
                return redirect("core:checkout")
        except ObjectDoesNotExist as e:
            messages.error(self.request , "You don't have any active order")
            return redirect("core:cart-summary")



@login_required
def add_quantity(request , slug):
    item = get_object_or_404(Item , slug = slug)
    order = Order.objects.get(user = request.user , ordered =False)
    orderItem = order.items.get(item = item , ordered = False, user = request.user)
    orderItem.quantity +=1
    orderItem.save()
    messages.success(request , "We have increased the quantity ")
    return redirect("core:cart-summary")

@login_required
def minus_quantity(request, slug):
    item = get_object_or_404(Item , slug = slug)
    order = Order.objects.get(user = request.user , ordered =False)
    if order.items.filter(item__slug = slug ).exists():
        orderItem = OrderItem.objects.get(
        user = request.user ,
        ordered = False,
        item = item)
        if orderItem.quantity !=1:
            orderItem.quantity -= 1
            orderItem.save()
            messages.success(request , "Product quantity decreased")
        else:
            orderItem.delete()
        messages.success(request , "Product removed from Cart ")
        return redirect("core:cart-summary")
    else:
        messages.error( request ,"You havn't purcahsed any product like this ")
        return redirect("core:cart-summary")

@login_required
def delete_product(request, slug):
    item = get_object_or_404(Item , slug = slug)
    order = Order.objects.get(user = request.user , ordered =False)
    if order.items.filter(item__slug = slug ).exists():
        orderItem = OrderItem.objects.get(
        user = request.user ,
        ordered = False,
        item = item)
        orderItem.delete()
        messages.success(request , "Product removed from Cart ")
        return redirect("core:cart-summary")
    else:
        messages.error( request ,"You havn't purcahsed any product like this ")
        return redirect("core:cart-summary")


class OrderSummary(LoginRequiredMixin,DetailView):
    def get(self , *args , **kwargs):
        user =self.request.user
        try:
            order =Order.objects.get( user = user , ordered = False)
            context= {
                'order':order
            }
            return render(self.request ,"cart_summary.html", context)
        except ObjectDoesNotExist as e:
            messages.error(self.request , "You don't have any active order")
            return redirect("/")
class PaymentView(View):
    def get(self , *args , **kwargs):
        order = Order.objects.get(user = self.request.user , ordered =False)
        context = {
            'order': order
        }
        return render(self.request , "payment-page.html" , context)
    def post(self, *args, **kwaargs):
        order = Order.objects.get(user = self.request.user , ordered =False)
        token = self.request.POST.get('stripeToken')
        print("POST pramatre are : {}".format(self.request.POST))
        print("Token is : ".format(token))
        try:
            charge = stripe.Charge.create(
            currency ='eur', source =token, amount =int(order.get_total_amount())*100
            )
            payment  = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total_amount()*100
            payment.save()
            order.ordered = True
            order.payment = payment
            order.save()
            for orderItem in order.items.all():
                orderItem.ordered = True
                orderItem.save()
            messages.success(self.request, "Your order has been successfull")
            return redirect('/')
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            messages.error(self.request , e.error.message)
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request ,"API ")
            return redirect('/')
        except stripe.error.InvalidRequestError as e:
            messages.error(self.request ,"API ")
            return redirect('/')
        except stripe.error.AuthenticationError as e:
            messages.error(self.request ,"API ")
            return redirect('/')
        except stripe.error.APIConnectionError as e:
            messages.error(self.request ,"API ")
            return redirect('/')
        except stripe.error.StripeError as e:
            messages.error(self.request ,"API ")
            return redirect('/')
        except Exception as e:
            print(e)
            messages.error(self.request ,"API ")
            return redirect('/')
