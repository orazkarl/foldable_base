from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout



def logout_user(request):
    logout(request)
    return redirect('account_login')
