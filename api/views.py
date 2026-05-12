import pandas as pd
import numpy as np
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.cache import cache
from django.template.loader import render_to_string
from dashboard.models import Dashboard

def get_filters(request, dashboard_id):
    cache_key = f'filters_{dashboard_id}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return JsonResponse({'filters': cached_data})
    
    dashboard = get_object_or_404(Dashboard, id=dashboard_id)
    
    file_path = dashboard.dataset.file.path
    if dashboard.dataset.file_type == 'csv':
        df = pd.read_csv(file_path, encoding='utf-8')
    else:
        df = pd.read_excel(file_path)
    
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    filters = []
    for col in categorical_cols[:4]:
        unique_values = df[col].dropna().unique().tolist()
        if len(unique_values) <= 20:
            filters.append({
                'column': col,
                'label': col.replace('_', ' ').title(),
                'values': unique_values[:15]
            })
    
    cache.set(cache_key, filters, 300)
    return JsonResponse({'filters': filters})

def get_main_chart(request, dashboard_id):
    # Create cache key with filters
    filter_string = '_'.join([f"{k}={v}" for k, v in request.GET.items() if v and v != 'all'])
    cache_key = f'main_chart_{dashboard_id}_{filter_string}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return JsonResponse(cached_data)
    
    dashboard = get_object_or_404(Dashboard, id=dashboard_id)
    
    file_path = dashboard.dataset.file.path
    if dashboard.dataset.file_type == 'csv':
        df = pd.read_csv(file_path, encoding='utf-8')
    else:
        df = pd.read_excel(file_path)
    
    # Apply filters
    for key, value in request.GET.items():
        if value and value != 'all' and key in df.columns:
            df = df[df[key] == value]
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    result = {'labels': [], 'values': [], 'title': 'No data available', 'x_label': '', 'y_label': ''}
    
    if categorical_cols and numeric_cols:
        group_col = categorical_cols[0]
        value_col = numeric_cols[0]
        chart_data = df.groupby(group_col)[value_col].mean().sort_values(ascending=False).head(15)
        
        result = {
            'labels': chart_data.index.tolist(),
            'values': chart_data.values.tolist(),
            'title': f'{value_col.replace("_", " ").title()} by {group_col.replace("_", " ").title()}',
            'x_label': group_col.replace('_', ' ').title(),
            'y_label': value_col.replace('_', ' ').title()
        }
    
    cache.set(cache_key, result, 120)
    return JsonResponse(result)

def get_pie_chart(request, dashboard_id):
    filter_string = '_'.join([f"{k}={v}" for k, v in request.GET.items() if v and v != 'all'])
    cache_key = f'pie_chart_{dashboard_id}_{filter_string}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return JsonResponse(cached_data)
    
    dashboard = get_object_or_404(Dashboard, id=dashboard_id)
    
    file_path = dashboard.dataset.file.path
    if dashboard.dataset.file_type == 'csv':
        df = pd.read_csv(file_path, encoding='utf-8')
    else:
        df = pd.read_excel(file_path)
    
    for key, value in request.GET.items():
        if value and value != 'all' and key in df.columns:
            df = df[df[key] == value]
    
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    result = {'labels': [], 'values': [], 'title': 'No categorical data'}
    
    if categorical_cols:
        chart_data = df[categorical_cols[0]].value_counts().head(8)
        result = {
            'labels': chart_data.index.tolist(),
            'values': chart_data.values.tolist(),
            'title': f'{categorical_cols[0].replace("_", " ").title()} Distribution'
        }
    
    cache.set(cache_key, result, 120)
    return JsonResponse(result)

def get_trend_chart(request, dashboard_id):
    filter_string = '_'.join([f"{k}={v}" for k, v in request.GET.items() if v and v != 'all'])
    cache_key = f'trend_chart_{dashboard_id}_{filter_string}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return JsonResponse(cached_data)
    
    dashboard = get_object_or_404(Dashboard, id=dashboard_id)
    
    file_path = dashboard.dataset.file.path
    if dashboard.dataset.file_type == 'csv':
        df = pd.read_csv(file_path, encoding='utf-8')
    else:
        df = pd.read_excel(file_path)
    
    for key, value in request.GET.items():
        if value and value != 'all' and key in df.columns:
            df = df[df[key] == value]
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    result = {'labels': [], 'values': [], 'title': 'No trend data available', 'x_label': 'Index', 'y_label': 'Value'}
    
    if numeric_cols and len(df) > 0:
        values = df[numeric_cols[0]].values[:50]
        result = {
            'labels': list(range(1, len(values) + 1)),
            'values': values.tolist(),
            'title': f'{numeric_cols[0].replace("_", " ").title()} Trend',
            'x_label': 'Sequence',
            'y_label': numeric_cols[0].replace('_', ' ').title()
        }
    
    cache.set(cache_key, result, 120)
    return JsonResponse(result)

def get_top_chart(request, dashboard_id):
    filter_string = '_'.join([f"{k}={v}" for k, v in request.GET.items() if v and v != 'all'])
    cache_key = f'top_chart_{dashboard_id}_{filter_string}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return JsonResponse(cached_data)
    
    dashboard = get_object_or_404(Dashboard, id=dashboard_id)
    
    file_path = dashboard.dataset.file.path
    if dashboard.dataset.file_type == 'csv':
        df = pd.read_csv(file_path, encoding='utf-8')
    else:
        df = pd.read_excel(file_path)
    
    for key, value in request.GET.items():
        if value and value != 'all' and key in df.columns:
            df = df[df[key] == value]
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    result = {'labels': [], 'values': [], 'title': 'No top data available', 'x_label': 'Value', 'y_label': 'Category'}
    
    if categorical_cols and numeric_cols:
        top_data = df.groupby(categorical_cols[0])[numeric_cols[0]].mean().sort_values(ascending=True).head(10)
        result = {
            'labels': top_data.index.tolist(),
            'values': top_data.values.tolist(),
            'title': f'Top 10 {categorical_cols[0].replace("_", " ").title()} by {numeric_cols[0].replace("_", " ").title()}',
            'x_label': numeric_cols[0].replace('_', ' ').title(),
            'y_label': categorical_cols[0].replace('_', ' ').title()
        }
    
    cache.set(cache_key, result, 120)
    return JsonResponse(result)

def get_kpi_update(request, dashboard_id):
    filter_string = '_'.join([f"{k}={v}" for k, v in request.GET.items() if v and v != 'all'])
    cache_key = f'kpi_update_{dashboard_id}_{filter_string}'
    cached_html = cache.get(cache_key)
    
    if cached_html:
        return JsonResponse({'html': cached_html})
    
    dashboard = get_object_or_404(Dashboard, id=dashboard_id)
    
    file_path = dashboard.dataset.file.path
    if dashboard.dataset.file_type == 'csv':
        df = pd.read_csv(file_path, encoding='utf-8')
    else:
        df = pd.read_excel(file_path)
    
    for key, value in request.GET.items():
        if value and value != 'all' and key in df.columns:
            df = df[df[key] == value]
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if numeric_cols:
        kpis = [
            {'value': f'{df[numeric_cols[0]].mean():,.0f}', 'label': f'Avg {numeric_cols[0].replace("_", " ").title()}', 'trend': '+'},
            {'value': f'{len(df):,}', 'label': 'Total Records', 'trend': '+'},
            {'value': f'{df[numeric_cols[0]].max():,.0f}', 'label': f'Max {numeric_cols[0].replace("_", " ").title()}', 'trend': '+'},
            {'value': f'{df[numeric_cols[0]].min():,.0f}', 'label': f'Min {numeric_cols[0].replace("_", " ").title()}', 'trend': '='}
        ]
    else:
        kpis = [
            {'value': f'{len(df):,}', 'label': 'Total Records', 'trend': '+'},
            {'value': len(df.columns), 'label': 'Total Columns', 'trend': '='},
            {'value': 'N/A', 'label': 'Numeric Fields', 'trend': '+'},
            {'value': '100%', 'label': 'Data Quality', 'trend': '+'}
        ]
    
    html = render_to_string('dashboard/kpi_partial.html', {'kpis': kpis})
    cache.set(cache_key, html, 120)
    return JsonResponse({'html': html})

def get_ai_insights_view(request, dashboard_id):
    filter_string = '_'.join([f"{k}={v}" for k, v in request.GET.items() if v and v != 'all'])
    cache_key = f'ai_insights_{dashboard_id}_{filter_string}'
    cached_insights = cache.get(cache_key)
    
    if cached_insights:
        return JsonResponse({'insights': cached_insights})
    
    dashboard = get_object_or_404(Dashboard, id=dashboard_id)
    
    file_path = dashboard.dataset.file.path
    if dashboard.dataset.file_type == 'csv':
        df = pd.read_csv(file_path, encoding='utf-8')
    else:
        df = pd.read_excel(file_path)
    
    for key, value in request.GET.items():
        if value and value != 'all' and key in df.columns:
            df = df[df[key] == value]
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    insights = [
        {'type': 'info', 'icon': 'database', 'text': f'Dataset contains {len(df):,} records and {len(df.columns)} columns'},
        {'type': 'success', 'icon': 'check-circle', 'text': f'Data quality: {100 - (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100):.1f}% complete'},
    ]
    
    if numeric_cols:
        insights.append({
            'type': 'primary',
            'icon': 'chart-line',
            'text': f'Average {numeric_cols[0]}: {df[numeric_cols[0]].mean():,.2f}'
        })
    
    if categorical_cols and len(df) > 0 and len(df[categorical_cols[0]].value_counts()) > 0:
        top_cat = df[categorical_cols[0]].value_counts().index[0]
        insights.append({
            'type': 'info',
            'icon': 'chart-pie',
            'text': f'Most common {categorical_cols[0]}: {top_cat}'
        })
    
    insights.append({
        'type': 'primary',
        'icon': 'lightbulb',
        'text': 'Use filters above to explore specific segments'
    })
    
    cache.set(cache_key, insights, 300)
    return JsonResponse({'insights': insights})