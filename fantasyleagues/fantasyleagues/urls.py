"""fantasyleagues URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from yahoo_leagues.views import LoginView, AuthView, HomeView, YahooAuth, SuccessView, ShowLeague

urlpatterns = [
    url(r'^admin/', admin.site.urls, name="admin"),
    url(r'^login/$', LoginView.as_view(), name="login"),
    url(r'^home/$', HomeView.as_view(), name="home"),
    url(r'^yahoo_auth/$', YahooAuth.as_view(), name="yahoo_auth"),
    url(r'^auth/$', AuthView.as_view(), name="auth"), 
    url(r'^show_leagues/$', ShowLeague.as_view(), name="show_league"), 
    url(r'^success/$', SuccessView.as_view(), name="success")
]
