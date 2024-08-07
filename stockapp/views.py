from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.contrib import messages
from django.utils import timezone
from .forms import *
from django.utils import translation
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

# Create your views here.
@login_required
def home(request):
    translation.activate(request.user.profile.language)
    get_total_items_type = Product.objects.all().count()
    get_total_system_users = User.objects.all().count()
    get_total_requests = Requests.objects.all().count()
    get_total_approved_request = Requests.objects.filter(request_status=True).count()
    get_user_total_requests = Requests.objects.filter(requested_by=request.user).count()
    get_user_total_approved_request = Requests.objects.filter(requested_by=request.user, request_status=True).count()

    items_data = []
    get_products = Product.objects.all()
    if get_products:
        for item in Product.objects.all():
            data = {}
            data['item'] = item
            get_item_proved_request_quantity_sum = Requests.objects.filter(item_name=item, request_status=True, returned_date__isnull=True).aggregate(approved_quantity = Sum('quantity'))
            if get_item_proved_request_quantity_sum['approved_quantity']:
                available_quantity = item.quantity - int(get_item_proved_request_quantity_sum['approved_quantity'])
                data['used_quantity'] = get_item_proved_request_quantity_sum['approved_quantity']
                data['available_quantity'] = available_quantity
                items_data.append(data)

            else:
                data['used_quantity'] = 0
                available_quantity = item.quantity
                data['available_quantity'] = available_quantity
                items_data.append(data)

            # < ---------- SENDMAIL IF AVAILABLE LESS THA 10 ---------->
            if available_quantity <= 10:
                html_template = 'stockapp/message.html'

                html_message = render_to_string(html_template, { 'available_quantity': available_quantity, 'item':item})

                subject = 'wisdsol STOCK MANAGER ALERT'
                from_email = 'lovjes4@gmail.com'
                to_email = ['wisdsoltech@gmail.com']

                message = EmailMessage(subject, html_message, from_email, to_email)
                message.content_subtype = 'html'
                message.send()


    get_requests_made = Requests.objects.filter(requested_by = request.user).order_by('-requested_date')
    template_name = 'stockapp/home.html'
    context = {
        'total_items_type':get_total_items_type,
        'total_system_users':get_total_system_users,
        'total_requests':get_total_requests,
        'total_approved_request':get_total_approved_request,
        'user_total_requests':get_user_total_requests,
        'user_total_approved_request':get_user_total_approved_request,
        'items_data':items_data,
        'requests_made':get_requests_made,
    }
    return render(request, template_name, context)

@login_required
def profile(request):
    translation.activate(request.user.profile.language)
    get_user = get_object_or_404(User, username = request.user)
    template_name = 'stockapp/profile.html'
    context = {
        'user': get_user,
    }
    return render(request, template_name, context)

@login_required
def systemUsers(request):
    translation.activate(request.user.profile.language)
    form = ProfileForm()
    if request.method == 'POST':
        form = ProfileForm(request.POST or None)
        get_user_id = form.data['user']
        get_role_name = form.data['role_name']
        get_user = get_object_or_404(User, pk=get_user_id)
        if not get_user.profile:
            if form.is_valid():
                form.save()
        else:
            Profile.objects.filter(user=get_user).update(
                role_name = get_role_name
            )
            messages.success(request, f'Query OK, Role assigned succesifully')
            return redirect('dashboard:systemUsers')
    template_name = 'stockapp/systemUsers.html'
    get_users = User.objects.all().order_by('first_name')
    context = {
        'form':form,
        'users':get_users,
    }
    return render(request, template_name, context)

@login_required
def manageProducts(request):
    translation.activate(request.user.profile.language)
    if request.method == 'POST' and 'new_button' in request.POST:
        form = ProductForm(request.POST or None)
        if form.is_valid():
            instance = form.save(commit = False)
            instance.created_by = request.user
            instance.save()
            messages.success(request, f'New Item added succesifully')
            return redirect('dashboard:manageProducts')

    elif request.method == 'POST' and 'existing_button' in request.POST:
        existing_form = ExistingProductForm(request.POST or None)
        get_item_name = existing_form.data['name']
        get_quantity = existing_form.data['quantity']
        get_item = Product.objects.get(pk=get_item_name)
        if existing_form.is_valid():
            instance = existing_form.save(commit = False)
            instance.created_by = request.user
            new_quantity = get_item.quantity + int(get_quantity)
            instance.save()
            Product.objects.filter(pk=get_item_name).update(
                quantity = new_quantity
            )
            messages.success(request, f'{get_item.name.upper()} Items added succesifully')
            return redirect('dashboard:manageProducts')

    get_products = Product.objects.all().order_by('created_date')
    form = ProductForm()
    existing_form = ExistingProductForm()
    template_name = 'stockapp/manageProduct.html'
    context = {
        'form':form,
        'existing_form':existing_form,
        'products':get_products,
    }
    return render(request, template_name, context)

@login_required
def requestItem(request):
    translation.activate(request.user.profile.language)
    if request.method == 'POST':
        form = RequestForm(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.requested_by = request.user
            instance.save()
            messages.success(request, 'Your request was submitted successifully')
            return redirect('dashboard:home')

    form = RequestForm()
    template_name = 'stockapp/request.html'
    context = {
        'form':form,
    }
    return render(request, template_name, context)

@login_required
def stockRequests(request):
    translation.activate(request.user.profile.language)
    get_requests_made = Requests.objects.filter().order_by('-requested_date')
    template_name = 'stockapp/stockRequests.html'
    context = {
        'requests_made':get_requests_made,
    }
    return render(request, template_name, context)

@login_required
def stockRequestsApprove(request, pk):
    translation.activate(request.user.profile.language)
    get_request = get_object_or_404(Requests, pk=pk)
    Requests.objects.filter(pk=pk).update(
        request_status = True,
        approved_date = timezone.now()
    )
    messages.warning(request, 'Request approved succesifully')
    return redirect('dashboard:stockRequests')

@login_required
def stockReturn(request, pk):
    translation.activate(request.user.profile.language)
    get_request = get_object_or_404(Requests, pk=pk)
    Requests.objects.filter(pk=pk).update(
        returned_date = timezone.now()
    )
    messages.warning(request, 'Items marked as returned succesifully')
    return redirect('dashboard:stockRequests')
