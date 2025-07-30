from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from .models import (Transition)
from django.contrib.auth.decorators import login_required
from .forms import TransitionForm,UserForm
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.db import models
from django.db.models import Q,Sum
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Create your views here.


def Loginuser(request):
    if request.method == "POST":
        userform = UserForm(request.POST)

        if userform.is_valid():
            username = userform.cleaned_data["username"]
            password = userform.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request,user)
                return redirect("/finance/create")
            
            else:
                return render(request,"login.html",{'error':'invalid credintals'})

    else:
        userform = UserForm()
    
    return render(request,"login.html",{'form':userform})
    

                

@login_required
def Posttranisiton(request):
    if request.method == "POST":
        form = TransitionForm(request.POST)

        if form.is_valid():
            transiton = form.save(commit=False)
            transiton.user = request.user
            transiton.save()

            return redirect("/")
    else:
        form = TransitionForm() 
    return render(request,'Posttransition.html', {'form': form})


@login_required
def Gettransition(request):
    filter_type = request.GET.get('type')
    if filter_type in ['income', 'expense']:
        transitions = Transition.objects.filter(type=filter_type, user=request.user.id).order_by('-date')
    else:
        transitions = Transition.objects.filter(user=request.user.id).order_by('-date')
    
    return render(request, 'get_transition.html', {'transitions': transitions})


from django.shortcuts import render, redirect
from django.db.models import Q, Sum
from django.contrib.auth.decorators import login_required
from .forms import TransitionForm  # Make sure you have this form imported
from .models import Transition
from django.utils.timezone import now

@login_required
def dashboard(request):

    if request.method == "POST":
        form = TransitionForm(request.POST)
        if form.is_valid():
            transition = form.save(commit=False)
            transition.user = request.user
            transition.save()
            return redirect('dashboard')  # Use named URL for better maintainability
        else:
            # Render with form errors and existing context later
            pass
    else:
        form = TransitionForm()

    # Filter parameters from GET
    type = request.GET.get('type')
    month = request.GET.get('month')
    year = request.GET.get('year')
    min_amount = request.GET.get('min_amount')
    max_amount = request.GET.get('max_amount')
    user = request.user

    filters = Q(user=user)

    months = [
        ('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
        ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'),
        ('09', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
    ]

    years = ['2023', '2024', '2025']

    if type in ['income', 'expense']:
        filters &= Q(type=type)

    if month:
        filters &= Q(date__month=month)
    if year:
        filters &= Q(date__year=year)

    if min_amount:
        try:
            min_amount_val = float(min_amount)
            filters &= Q(amount__gte=min_amount_val)
        except ValueError:
            pass

    if max_amount:
        try:
            max_amount_val = float(max_amount)
            filters &= Q(amount__lte=max_amount_val)
        except ValueError:
            pass

    transactions = Transition.objects.filter(filters).order_by('-date')

    # Calculate totals with same filters except type (for accurate sums)
    total_income_filters = Q(user=user, type='income')
    total_expense_filters = Q(user=user, type='expense')

    if month:
        total_income_filters &= Q(date__month=month)
        total_expense_filters &= Q(date__month=month)
    if year:
        total_income_filters &= Q(date__year=year)
        total_expense_filters &= Q(date__year=year)
    if min_amount:
        try:
            total_income_filters &= Q(amount__gte=min_amount_val)
            total_expense_filters &= Q(amount__gte=min_amount_val)
        except:
            pass
    if max_amount:
        try:
            total_income_filters &= Q(amount__lte=max_amount_val)
            total_expense_filters &= Q(amount__lte=max_amount_val)
        except:
            pass

    total_income = Transition.objects.filter(total_income_filters).aggregate(total=Sum('amount'))['total'] or 0
    total_expense = Transition.objects.filter(total_expense_filters).aggregate(total=Sum('amount'))['total'] or 0

    if type == 'income':
        total = total_income
    elif type == 'expense':
        total = total_expense
    else:
        total = total_income - total_expense

    context = {
        'form': form,                 
        'type': type,
        'month': month,
        'year': year,
        'min_amount': min_amount,
        'max_amount': max_amount,
        'total_income': total_income,
        'total_expense': total_expense,
        'total': total,
        'transactions': transactions,
        'months': months,
        'years': years,
    }

    return render(request, 'dashboard.html', context)


@csrf_exempt
@login_required
def single_transitionpage(request, transaction_id):
    transaction = get_object_or_404(Transition, id=transaction_id, user=request.user)

    if request.method == "DELETE":
        transaction.delete()
        return JsonResponse({"success": True})

    elif request.method == "PUT":
        import json
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

        form = TransitionForm(data, instance=transaction)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    else:
        form = TransitionForm(instance=transaction)
        return render(request, "single_transaction.html", {
            "transaction": transaction,
            "form": form,
        })

def bar_graph(request):
    user = request.user

    income_by_month = (
        Transition.objects.filter(user=user, type='income')
        .values('date__month')
        .annotate(total=Sum('amount'))
        .order_by('date__month')
    )
    expense_by_month = (
        Transition.objects.filter(user=user, type='expense')
        .values('date__month')
        .annotate(total=Sum('amount'))
        .order_by('date__month')
    )

    months = [
        ('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
        ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'),
        ('09', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December'),
    ]

    # Extract just month names for chart labels
    month_names = [name for val, name in months]

    income_data = [0] * 12
    expense_data = [0] * 12

    for item in income_by_month:
        income_data[item['date__month'] - 1] = float(item['total'])

    for item in expense_by_month:
        expense_data[item['date__month'] - 1] = float(item['total'])

    context = {
        'month_names': json.dumps(month_names),  # JSON string for JS labels
        'income_data': json.dumps(income_data),  # JSON string for JS income data
        'expense_data': json.dumps(expense_data),  # JSON string for JS expense data
    }

    return render(request, "bar_chart.html", context)

def pie_chart(request):
    user = request.user

    income_total = (
        Transition.objects.filter(user=user, type='income')
        .aggregate(total=Sum('amount'))['total'] or 0
    )
    expense_total = (
        Transition.objects.filter(user=user, type='expense')
        .aggregate(total=Sum('amount'))['total'] or 0
    )

    labels = ['Income', 'Expense']
    data = [float(income_total), float(expense_total)]

    context = {
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'income_total': income_total,
        'expense_total': expense_total,
    }
    return render(request, "pie_chart.html", context)

