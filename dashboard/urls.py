from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [

    path('', views.index_view, name='index'),

    path('create/', views.create_view, name='create'),

    path(
        'view/<int:dashboard_id>/',
        views.view_dashboard,
        name='view'
    ),

    path(
        'delete/<int:dashboard_id>/',
        views.delete_dashboard,
        name='delete'
    ),

    path(
        'duplicate/<int:dashboard_id>/',
        views.duplicate_dashboard,
        name='duplicate'
    ),

    path(
        'send-report/<int:dashboard_id>/',
        views.send_report_email,
        name='send_report_email'
    ),
]