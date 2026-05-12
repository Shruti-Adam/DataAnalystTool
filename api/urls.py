
from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('filters/<int:dashboard_id>/', views.get_filters, name='filters'),
    path('main-chart/<int:dashboard_id>/', views.get_main_chart, name='main_chart'),
    path('pie-chart/<int:dashboard_id>/', views.get_pie_chart, name='pie_chart'),
    path('trend-chart/<int:dashboard_id>/', views.get_trend_chart, name='trend_chart'),
    path('top-chart/<int:dashboard_id>/', views.get_top_chart, name='top_chart'),
    path('kpi-update/<int:dashboard_id>/', views.get_kpi_update, name='kpi_update'),
    path('ai-insights/<int:dashboard_id>/', views.get_ai_insights_view, name='ai_insights'),
]
