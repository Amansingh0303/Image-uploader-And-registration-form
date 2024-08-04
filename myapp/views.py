from django.shortcuts import render, HttpResponseRedirect,redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import authenticate ,login, logout,update_session_auth_hash
from django.contrib import messages
from django.core.cache import cache
import smtplib,random
from .forms import ImageForm
from . models import Image

############################### Home form ############################

def home(request):
    img = Image.objects.all()
    return render(request,'myapp/home.html',{'img':img})













############################ Signup Form ###############################


def signup_form(request):
    if request.method == "POST":
        uname=request.POST.get('username')
        fname=request.POST.get('name')
        lname=request.POST.get('lastname')
        email=request.POST.get('email')
        upass=request.POST.get('password')
        passwords=request.POST.get('passwords')
        first = User.objects.filter(username = uname).first()
        
        if first is None :
            if upass == passwords:
                user = User(first_name =fname ,last_name=lname, username=uname, email= email)
                user.set_password(upass)
                cache.set('user',user,70)
                cache.set('email',email,70)
                get(request,email)
                cache.set('verify', 'verify',70)
                messages.success(request,'Otp Send')
                return redirect('/otp/')
            else:
                messages.warning(request,"Password din't match , Please enter correct Password")
                return redirect('/signup/')
        else:
            messages.warning(request,'Username Already Exist , Please Enter Different Username')
            return redirect('/signup/')

        # fm=User.objects.filter(username=uname).first()
        # if fm ==None:
        #     user=User(first_name=fname,last_name=lname,username=uname,email=email)
        #     user.set_password(upass)
        #     messages.success(request, 'Ceate Account Successfully !! ')
        #     user.save()
        #     return redirect('/login/')
        # else:
        #     return redirect('/signup/' )
       
    return render(request,'myapp/signup.html' )


###############################    Otp views ############################################# 

def ot(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        if otp != None:
            mv = cache.get('otp')
            if otp == mv:
                user = cache.get('user')
                user.save()
                cache.clear
                messages.success(request, 'Account Created Successfully ')
                return redirect('/login/')
            else:
                messages.warning(request, 'Please enter Correct otp')
                return redirect('/otp/')
        else:
            messages.warning(request, 'Please enter otp')
            return redirect ('/otp/')
    else:
        return redirect('/otp/')


def resend(request):
    email = cache.get('email')
    if email  != None:

        time = cache.get('time')

        if time != '60':
            if email != None:
                get(request,email)
                messages.success(request,'Resend otp successfully')
                return redirect('/otp/')
            else:
                messages.warning(request, 'Youre session expire')
                return redirect('/signup/')
        else:
            messages.warning(request,'Resend otp after 60 second')
            return redirect('/otp/')
    else:
        return redirect('/signup/')
    

def  get(request ,email):
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login('amansinghaira137@gmail.com','tcmuymcxgaqkphnf')
    otp = str(random.randint(1000,9999))
    cache.set('otp',otp,60)
    cache.set('time','60',60)
    msg = 'Hello , Youre OTP ' +str(otp)
    server.sendmail('amansinghaira137@gmail.com',email,msg)
    server.quit()


def otp(request):
    verify = cache.get('verify')
    if verify != None:
        return render(request, 'myapp/otp.html')
    # else:
        
        # return redirect('/signup/')



##############################################    Login form ##########################


def login_form(request):
 
    if not request.user.is_authenticated:
          if request.method == 'POST':
              uname=request.POST.get('Username')
              upass=request.POST.get('password')
              fm=User.objects.filter(username=uname).first()
              if fm != None:
                     user = authenticate(username =uname, password = upass)
                     login(request,user)
                     messages.success(request, 'Login Successfully !! ')
                     return redirect('/dashboard/')
              else:
                
                    messages.warning(request, 'user not found !! ')
                    return redirect('/dashboard/')
                     
          else:
              return render(request, 'myapp/login.html')
        
             
    else:
        return redirect('/signup/')
    



##############################  forget password #####################


def user_change_pass(request):
    if request.user.is_authenticated:
        if request.methode == 'POST':
            fm = SetPasswordForm( user=request.user , data= request.POST)
            if fm.is_valid():
                fm.save()
                update_session_auth_hash(request,fm.user)
                messages.success(request, 'Forgot Password Successfully !!')
                return redirect('/dashboard/')
        else:
            fm = SetPasswordForm(user = request.user)
        return render(request, 'myapp/forgot.html', {'form':fm} )
    else:
        return redirect('/login/')



##########################################  Image Uploader code #####################################
def dashboard(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form =ImageForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
        form = ImageForm()
        img = Image.objects.all()
        return render(request, 'myapp/dashboard.html',{'img':img,'form':form})
    else:
        return redirect('/login/')    



#############################  user_Logout  ############################################

def user_logout(request):
    logout(request)
    return redirect('/login/')
