import json

from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from board.models import Board, comment
from urllib.parse import quote
import os
# rest api 추가
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
# from api.serializer import MyTokenObtainPairSerializer, RegisterSerializer

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

UPLOAD_DIR='c:/ocupload/'

def login(request):#로그인
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

def home(request):#메인
    return render(request,'main.html')

def login_form(request):#로그인 창
    return render(request,'user/login.html')

def signup_form(request):#회원가입 창
    return render(request,'user/signup.html')

@csrf_exempt
def signup(request):#회원가입
    if request.method=='POST':
        if request.POST['password']==request.POST['password2']:
            username=request.POST['username']
            password=request.POST['password']
            email=request.POST['email']
            user=User.objects.create_user(username,email,password)
            return redirect("/login_form/")
    return render(request,'user/signup.html')

# 로그인 테스트
def signin(request):#로그인
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

#  유저 등록 테스트
def signupTest(request):
    if request.method=='POST':
        if request.POST['password']==request.POST['password2']:
            username=request.POST['username']
            password=request.POST['password']
            email=request.POST['email']
            user=User.objects.create_user(username, email, password)
        return JsonResponse({'message': 'User registered successfully'})

def logout(request):#로그아웃
    if request.user.is_authenticated:
        auth.logout(request)
        return redirect('/login_form')
    return render(request,'user/main.html')

def list(request):#게시판 목록
    boardCount=Board.objects.count()
    boardList=Board.objects.all().order_by("-idx")
    return render(request,"board/list.html",
                  {"boardList":boardList,"boardCount":boardCount})

# 1013 추가 model을 json 형태로 변경
def boardToJson(board):
    jsonData = []
    for data in board:
        dictionary = {
            "idx" : data.idx,
            "writer": data.writer,
            "title": data.title,
            "hit" : data.hit,
            "content":data.content,
            "post_date" : data.post_date.strftime("%Y-%m-%d %H:%M:%S"),
            "filename" : data.filename,
            "filesize": data.filesize,
            "down" : data.down
        }
        jsonData.append(dictionary)

    return json.dumps(jsonData)
# 상세페이지 정보를 json으로
def boardDetailToJson(board):

    if board == None:
        return None

    dictionary = {}
    dictionary["idx"] = board.idx
    dictionary["title"] = board.title
    dictionary["hit"] = board.hit
    dictionary["content"] = board.content

    return json.dumps(dictionary)
def lists(request): # list 목록 json 형태로 받아옴
    boardData = Board.objects.all()
    boardJsonData = boardToJson(boardData)

    return HttpResponse(boardJsonData, content_type='application/json')

def listDetail(request, page):
    boardData = Board.objects.get(idx = page)
    boardJsonData = boardDetailToJson(boardData)
    return HttpResponse(boardJsonData, content_type='application/json')

def write(request):#글쓰기
    return render(request,"board/write.html")

@csrf_exempt#저장
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

def download(request):
    id=request.GET['idx']
    dto=Board.objects.get(idx=id)
    path=UPLOAD_DIR+dto.filename
    filepath = os.path.basename(path)
    filepath = quote(filepath)
    with open(path, 'rb') as file:
        response = HttpResponse(file.read(),
                                content_type='application/actet-stream')
        response['Content-Disposition'] = "attachment;filename*=UTF-8''{0}".format(filepath)

    dto.down_up()
    dto.save()
    return response

def detail(request):
    id=request.GET['idx']
    dto=Board.objects.get(idx=id)
    dto.hit_up()
    dto.save()
    commentList=comment.objects.filter(board_idx=id).order_by("-idx")
    fsize="%.2f"%(dto.filesize/1024)
    return render(request,"board/detail.html",{'dto':dto,'fsize':fsize,
                  'commentList':commentList})

@csrf_exempt
def reply_insert(request):
    id=request.POST['idx']
    dto=comment(board_idx=id,
                writer=request.POST['writer'],
                content=request.POST['content'])
    dto.save()
    return redirect("/detail?idx="+id)

def delete(request):
    id=request.POST['idx']
    Board.objects.get(idx=id).delete()
    return redirect("/list/")

def update(request):
    id=request.POST['idx']
    dto_src=Board.objects.get(idx=id)
    fname=dto_src.filename
    fsize=dto_src.filesize

    if 'file' in request.FILES:
        file=request.FILES['file']
        fname=file.name
        fsize=file.size
        fp=open('%s%s'%(UPLOAD_DIR,fname),'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()

    dto_new=Board(idx=id,
                  writer=request.POST['writer'],
                  title=request.POST['title'],
                  content=request.POST['content'],
                  hit=dto_src.hit,
                  down=dto_src.down,
                  post_date=dto_src.post_date,
                  filename=fname, filesize=fsize)
    dto_new.save()
    return redirect("/list/")

# restapi
# class MyTokenObtainPairView(TokenObtainPairView):
#     serializer_class = MyTokenObtainPairSerializer
#
# class RegisterView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     permission_classes = (AllowAny,)
#     serializer_class = RegisterSerializer

@api_view(['GET'])
def getRoutes(request):
    routes = [
        'api/token',
        'api/register',
        'api/token/refresh',
    ]
    return Response(routes)

