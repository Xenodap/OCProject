from django.contrib import admin
from django.urls import path,include
from board import views

urlpatterns = [
    path('home/',views.home),
    path('admin/', admin.site.urls),
    # restapi 설정하기
    path('api/',include('rest_framework.urls')),


    path('signup/',views.signup),
    path('signup_form/',views.signup_form),
    path('login/',views.login),
    path('login_form/',views.login_form),
    path('logout/',views.logout),
    path('list/',views.list),
    path('write/',views.write),
    path('insert/',views.insert),
    path('download/',views.download),
    path('detail/',views.detail),
    path('reply_insert/',views.reply_insert),
    path('update/',views.update),
    path('delete/',views.delete),



]
