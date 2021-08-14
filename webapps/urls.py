"""webapps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from cryptocurrency import views

urlpatterns = [
	path('', views.home_action),
	path('oauth/', include('social_django.urls', namespace='social')),
	path('logout', auth_views.logout_then_login, name='logout'),
	path('home', views.home_action, name='home'),
	path('cryptocurrency/<str:ticker>', views.cryptocurrency_action, name='cryptocurrency'),
	path('back_door/<str:ticker>', views.back_door_action),
	path('watchlist', views.watchlist_action, name='watchlist'),
	path('deposit', views.deposit_action, name='deposit'),
	path('history', views.history_action, name='history'),
	path('update-price', views.update_price, name='update-price'),
	path('update-news', views.update_news, name='update-news'),
	path('balance-position',views.balance_and_position_action,name='balance-position'),
	path('watch/<str:ticker>', views.watch_action, name='watch'),
	path('unwatch/<str:ticker>', views.unwatch_action, name='unwatch'),
	path('search', views.search_action, name='search'),
    path('admin', admin.site.urls),
]
