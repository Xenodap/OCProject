from django.contrib import auth
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from board.models import Board


# Create your views here.

def index(request):
    return render(request, 'board/list.html')

def login(request):
    if request.method=="POST":
        username=request.POST['username']
        password=request.POST['password']
        user=auth.authenticate(request,username=username,password=password)

        if user is not None:
            auth.login(request,user)
            return redirect("/")
        else:
            return render(request,'user/login.html',{
                'error':'username or password is incorrect'
            })

    else:
        return render(request,'user/login.html')

def home(request):
    return render(request,'main.html')

def login_form(request):
    return render(request,'user/login.html')

def signup_form(request):
    return render(request,'user/signup.html')

@csrf_exempt
def signup(request):
    if request.method=='POST':
        if request.POST['password']==request.POST['password2']:
            username=request.POST['username']
            password=request.POST['password']
            email=request.POST['email']
            user=User.objects.create_user(username,email,password)
            return redirect("/login_form")
    return render(request,'user/signup.html')

def logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
        return redirect('/login_form')
    return render(request,'user/main.html')

def list(request):
    boardCount=Board.objects.count()
    boardList=Board.objects.all().order_by("-idx")
    return render(request,"board/ist.html",
                  {"boardList":boardList,"boardCount":boardCount})

def write(request):
    return render(request,"board/write.html")


UPLOAD_DIR='c:/ocupload/'
@csrf_exempt
def insert(request):
    fname=''
    fsize=0
    if 'file' in request.FILES:
        file=request.FILES['file']
        fname=file.name
        fsize=file.size

        fp=open('%s%s'%(UPLOAD_DIR,fname),'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()

    dto=Board(writer=request.POST['writer'],title=request.POST['title'],
              content=request.POST['content'],filename=fname,filesize=fsize)
    dto.save()
    print(dto)
    return redirect('/list')