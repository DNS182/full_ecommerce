from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.models import User 
from django.contrib.auth import authenticate,login


# Create your views here.
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email =  request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 == password2 :
            if User.objects.filter(username = username).exists():
                messages.error(request ,"OOPS, USER ALREADY EXISTS")
            elif User.objects.filter(email = email).exists():
                messages.error(request ,"OOPS, EMAIL WITH THAT USER ALREADY EXISTS")
            else:
                user = User.objects.create_user(username =username , email = email , password = password1)
                user.save()
                messages.success(request , "ACCOUNT CREATED SUCCESSFULLY.LOGIN :)")
                return redirect('/accounts/login')

        else:
            messages.error(request ,"PASSWORD DIDN'T MATCHED")


    return render(request ,'register.html' )

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username') 
        password1 = request.POST.get('password') 
        user = authenticate(username =username , password = password1) 
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request , "InValid Credentials")
    return render(request , 'login.html')

#logout used from django inbuilt logout feature ..


def error_404(request, exception):
    return render(request,'404.html')