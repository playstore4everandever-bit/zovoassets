from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import Step1Form, LoginForm
from .models import User, Wallet
from investments.models import InvestmentPlan, Investment


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "home.html")


def register_step1(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = Step1Form(request.POST)
        if form.is_valid():
            request.session["reg_step1"] = {
                "full_name": form.cleaned_data["full_name"],
                "email": form.cleaned_data["email"],
                "phone": form.cleaned_data["phone"],
                "password": form.cleaned_data["password"],
            }
            return redirect("register_step2")
    else:
        form = Step1Form()
    return render(request, "core/register_step1.html", {"form": form})


def register_step2(request):
    if not request.session.get("reg_step1"):
        return redirect("register")
    plans = InvestmentPlan.objects.filter(is_active=True)
    if request.method == "POST":
        plan_id = request.POST.get("plan_id")
        try:
            plan = InvestmentPlan.objects.get(id=plan_id, is_active=True)
            request.session["reg_step2"] = {"plan_id": plan.id}
            return redirect("register_step3")
        except InvestmentPlan.DoesNotExist:
            messages.error(request, "Please select a valid plan.")
    return render(request, "core/register_step2.html", {"plans": plans})


def register_step3(request):
    if not request.session.get("reg_step2"):
        return redirect("register_step2")
    plan = InvestmentPlan.objects.get(id=request.session["reg_step2"]["plan_id"])
    if request.method == "POST":
        amount_str = request.POST.get("amount", "0").replace(",", "")
        try:
            amount = float(amount_str)
        except ValueError:
            messages.error(request, "Enter a valid amount.")
            return render(request, "core/register_step3.html", {"plan": plan})
        if amount < float(plan.min_amount):
            messages.error(request, f"Minimum investment for {plan.name} is ${plan.min_amount:,.0f}.")
            return render(request, "core/register_step3.html", {"plan": plan})
        if plan.max_amount and amount > float(plan.max_amount):
            messages.error(request, f"Maximum investment for {plan.name} is ${plan.max_amount:,.0f}.")
            return render(request, "core/register_step3.html", {"plan": plan})
        step1 = request.session["reg_step1"]
        user = User.objects.create_user(
            email=step1["email"], password=step1["password"],
            full_name=step1["full_name"], phone=step1.get("phone", ""),
        )
        Wallet.objects.create(user=user)
        Investment.objects.create(user=user, plan=plan, amount=amount, status="pending")
        del request.session["reg_step1"]
        del request.session["reg_step2"]
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(request, f"Welcome {user.full_name}! Your investment is pending activation.")
        return redirect("dashboard")
    return render(request, "core/register_step3.html", {"plan": plan})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = LoginForm(request.POST, request=request)
        if form.is_valid():
            login(request, form.user)
            return redirect(request.GET.get("next", "dashboard"))
    else:
        form = LoginForm()
    return render(request, "core/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    user = request.user
    wallet = user.wallet
    investments = user.investments.select_related("plan").order_by("-created_at")
    loans = user.loans.order_by("-created_at")
    active_investment = investments.filter(status="active").first()
    pending_investment = investments.filter(status="pending").first()
    open_trades = user.trades.filter(status="open").select_related("asset") if hasattr(user, 'trades') else []
    trade_count = user.trades.count() if hasattr(user, 'trades') else 0
    return render(request, "core/dashboard.html", {
        "wallet": wallet,
        "investments": investments,
        "loans": loans,
        "active_investment": active_investment,
        "pending_investment": pending_investment,
        "open_trades": open_trades,
        "trade_count": trade_count,
    })
def contact(request):
    return render(request, "core/contact.html")

def about(request):
    return render(request, "core/about.html")

def careers(request):
    return render(request, "core/careers.html")


