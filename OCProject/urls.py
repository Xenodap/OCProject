from django.contrib import admin
from django.urls import path, include
from board import views
from django.template.loader import render_to_string

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('',views.home),
    path('admin/', admin.site.urls),
    # restapi 설정하기
    path('api/',include('rest_framework.urls')),
    # path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('register/', views.RegisterView.as_view(), name='auth_register'),
    path('', views.getRoutes),



    path('signup/',views.signup),
    path('signin/', views.signin),
    path('signup_form/',views.signup_form),
    path('signupTest/', views.signupTest, name = "signupTest"),
    path('csrf_token/', views.csrf_token_view, name='csrf_token_view'),
    path('login/',views.login),
    path('login_form/',views.login_form),
    path('logout/',views.logout),
    path('list/',views.list),
    path('test/', views.lists, name='lists'),
    path('list/<int:page>/',views.listDetail),
    path('write/',views.write),
    path('insert/',views.insert),
    path('download/',views.download),
    path('detail/',views.detail),
    path('reply_insert/',views.reply_insert),
    path('update/',views.update),
    path('delete/',views.delete),
    path('accounts/',include('allauth.urls')),



]
