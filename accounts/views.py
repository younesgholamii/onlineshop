from django.shortcuts import render, redirect
from django.views import View
from .forms import UserRegistrationForm, UserVerifyCodeForm, UserLoginForm
from utils import SendOtpCode
import random
from .models import OtpCode, User
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin



class UserRegisterView(View):
    form_class = UserRegistrationForm

    def get(self, request):
        form = self.form_class()
        return render(request, 'accounts/register.html', {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            random_code = random.randint(1000, 9999)
            SendOtpCode(form.cleaned_data['phone'], random_code)
            OtpCode.objects.create(phone_number=form.cleaned_data['phone'], code=random_code)
            request.session['user_registration_info'] = {
                'phone_number': form.cleaned_data['phone'],
                'email': form.cleaned_data['email'],
                'full_name': form.cleaned_data['full_name'],
                'password': form.cleaned_data['password'],
            }
            messages.success(request, 'we sent you a code', 'success')
            return redirect('accounts:verify_code')
        return render(request, 'accounts/register.html', {'form': form})


class UserRegisterVerifyView(View):
    form_class = UserVerifyCodeForm
    def get(self, request):
        form = self.form_class
        return render(request, 'accounts/verify.html', {'form': form})

    def post(self, request):
        user_session = request.session['user_registration_info']
        code_instance = OtpCode.objects.get(phone_number=user_session['phone_number'])
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if cd['code'] == code_instance.code:
                User.objects.create_user(user_session['phone_number'], user_session['email'], 
                                        user_session['full_name'], user_session['password'])
                code_instance.delete()
                messages.success(request, 'you registered successfully', 'success')
                return redirect('home:home')
            else:
                messages.error(request, 'this code is wrong', 'danger')
                return redirect('accounts:verify_code')
        return redirect('home:home')


class UserLoginView(View):
    form_class = UserLoginForm

    def get(self, request):
        form = self.form_class
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            random_code = random.randint(1000, 9999)
            SendOtpCode(form.cleaned_data['phone'], random_code)
            OtpCode.objects.create(phone_number=form.cleaned_data['phone'], code=random_code)
            request.session['user_login_info'] = {
                'phone_number': form.cleaned_data['phone'],
                'password': form.cleaned_data['password'],
            }
            messages.success(request, 'we sent you a code', 'success')
            return redirect('accounts:login_verify')
        return render(request, 'accounts/login.html', {'form': form})
    

class UserLoginVerifyView(View):
    form_class = UserVerifyCodeForm

    def get(self, request):
        form = self.form_class
        return render(request, 'accounts/verify.html', {'form': form})
    
    def post(self, request):
        user_session = request.session['user_login_info']
        form = self.form_class(request.POST)
        if form.is_valid():
            code_instance = OtpCode.objects.filter(phone_number=user_session['phone_number'])[0]
            cd = form.cleaned_data
            user = authenticate(request, phone_number=user_session['phone_number'], password=user_session['password'])
            if cd['code'] == code_instance.code:
                login(request, user)
                messages.success(request, 'logged in successfuly', 'success')
                code_instance.delete()
                return redirect('home:home')
            messages.error(request, 'code is not valid')
            return redirect('accounts:login_verify')
        return render(request, 'accounts/login.html', {'form': form})


class UserLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, 'logout successfully', 'success')
        return redirect('home:home')