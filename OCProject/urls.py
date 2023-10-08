from django.contrib import admin
from django.urls import path

from board import views

urlpatterns = [
    path('',views.home),
    path('admin/', admin.site.urls),


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
