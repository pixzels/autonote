from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('create/', views.CreateView.as_view(), name='create'),
    path('<uuid:id>/', views.DetailView.as_view(), name='detail'),
    path('<uuid:id>/delete', views.DeleteView.as_view(), name='delete'),
    path('create/', views.CreateView.as_view(), name='create'),
    path('summarize/', views.SummarizeView.as_view(), name='summarize')
]
