import pandas as pd
import numpy as np

from io import StringIO

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.cache import cache
from django.template.loader import render_to_string

from dashboard.models import Dashboard


# ============================================================
# CENTRAL DATAFRAME LOADER
# ============================================================

def load_dashboard_dataframe(dashboard):

    cache_key = f"dashboard_df_{dashboard.id}"

    cached_df_json = cache.get(cache_key)

    if cached_df_json:
        return pd.read_json(StringIO(cached_df_json))

    file_path = dashboard.dataset.file.path

    if dashboard.dataset.file_type == 'csv':

        df = pd.read_csv(
            file_path,
            encoding='utf-8',
            nrows=3000,
            low_memory=False
        )

    else:

        df = pd.read_excel(
            file_path,
            nrows=3000
        )

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(' ', '_')
    )

    cache.set(
        cache_key,
        df.to_json(),
        timeout=600
    )

    return df


# ============================================================
# APPLY FILTERS
# ============================================================

def apply_filters(df, request):

    for key, value in request.GET.items():

        if (
            value
            and value != 'all'
            and key in df.columns
        ):

            df = df[df[key].astype(str) == str(value)]

    return df


# ============================================================
# FILTERS API
# ============================================================

def get_filters(request, dashboard_id):

    dashboard = get_object_or_404(
        Dashboard,
        id=dashboard_id
    )

    df = load_dashboard_dataframe(dashboard)

    categorical_cols = df.select_dtypes(
        include=['object']
    ).columns.tolist()

    filters = []

    for col in categorical_cols[:4]:

        unique_values = (
            df[col]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        if len(unique_values) <= 20:

            filters.append({
                'column': col,
                'label': col.replace('_', ' ').title(),
                'values': unique_values[:15]
            })

    return JsonResponse({
        'filters': filters
    })


# ============================================================
# MAIN CHART
# ============================================================

def get_main_chart(request, dashboard_id):

    dashboard = get_object_or_404(
        Dashboard,
        id=dashboard_id
    )

    df = load_dashboard_dataframe(dashboard)

    df = apply_filters(df, request)

    numeric_cols = df.select_dtypes(
        include=[np.number]
    ).columns.tolist()

    categorical_cols = df.select_dtypes(
        include=['object']
    ).columns.tolist()

    if not categorical_cols or not numeric_cols:

        return JsonResponse({
            'labels': [],
            'values': [],
            'title': 'No Data'
        })

    group_col = categorical_cols[0]
    value_col = numeric_cols[0]

    chart_data = (
        df.groupby(group_col)[value_col]
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )

    return JsonResponse({
        'labels': chart_data.index.astype(str).tolist(),
        'values': chart_data.values.tolist(),
        'title': f'{value_col.title()} by {group_col.title()}'
    })


# ============================================================
# PIE CHART
# ============================================================

def get_pie_chart(request, dashboard_id):

    dashboard = get_object_or_404(
        Dashboard,
        id=dashboard_id
    )

    df = load_dashboard_dataframe(dashboard)

    df = apply_filters(df, request)

    categorical_cols = df.select_dtypes(
        include=['object']
    ).columns.tolist()

    if not categorical_cols:

        return JsonResponse({
            'labels': [],
            'values': []
        })

    chart_data = (
        df[categorical_cols[0]]
        .value_counts()
        .head(8)
    )

    return JsonResponse({
        'labels': chart_data.index.astype(str).tolist(),
        'values': chart_data.values.tolist()
    })


# ============================================================
# TREND CHART
# ============================================================

def get_trend_chart(request, dashboard_id):

    dashboard = get_object_or_404(
        Dashboard,
        id=dashboard_id
    )

    df = load_dashboard_dataframe(dashboard)

    df = apply_filters(df, request)

    numeric_cols = df.select_dtypes(
        include=[np.number]
    ).columns.tolist()

    if not numeric_cols:

        return JsonResponse({
            'labels': [],
            'values': []
        })

    values = df[numeric_cols[0]].head(50)

    return JsonResponse({
        'labels': list(range(1, len(values) + 1)),
        'values': values.tolist()
    })


# ============================================================
# TOP CHART
# ============================================================

def get_top_chart(request, dashboard_id):

    dashboard = get_object_or_404(
        Dashboard,
        id=dashboard_id
    )

    df = load_dashboard_dataframe(dashboard)

    df = apply_filters(df, request)

    numeric_cols = df.select_dtypes(
        include=[np.number]
    ).columns.tolist()

    categorical_cols = df.select_dtypes(
        include=['object']
    ).columns.tolist()

    if not numeric_cols or not categorical_cols:

        return JsonResponse({
            'labels': [],
            'values': []
        })

    chart_data = (
        df.groupby(categorical_cols[0])[numeric_cols[0]]
        .mean()
        .sort_values(ascending=True)
        .head(10)
    )

    return JsonResponse({
        'labels': chart_data.index.astype(str).tolist(),
        'values': chart_data.values.tolist()
    })


# ============================================================
# KPI API
# ============================================================

def get_kpi_update(request, dashboard_id):

    dashboard = get_object_or_404(
        Dashboard,
        id=dashboard_id
    )

    df = load_dashboard_dataframe(dashboard)

    df = apply_filters(df, request)

    numeric_cols = df.select_dtypes(
        include=[np.number]
    ).columns.tolist()

    if numeric_cols:

        kpis = [
            {
                'value': f'{len(df):,}',
                'label': 'Records',
                'trend': '+'
            },
            {
                'value': f'{df[numeric_cols[0]].mean():,.0f}',
                'label': 'Average',
                'trend': '+'
            },
            {
                'value': f'{df[numeric_cols[0]].max():,.0f}',
                'label': 'Maximum',
                'trend': '+'
            },
            {
                'value': f'{df[numeric_cols[0]].min():,.0f}',
                'label': 'Minimum',
                'trend': '='
            },
        ]

    else:

        kpis = [
            {
                'value': f'{len(df):,}',
                'label': 'Records',
                'trend': '+'
            }
        ]

    html = render_to_string(
        'dashboard/kpi_partial.html',
        {'kpis': kpis}
    )

    return JsonResponse({
        'html': html
    })


# ============================================================
# AI INSIGHTS
# ============================================================

def get_ai_insights_view(request, dashboard_id):

    dashboard = get_object_or_404(
        Dashboard,
        id=dashboard_id
    )

    df = load_dashboard_dataframe(dashboard)

    df = apply_filters(df, request)

    insights = [
        {
            'icon': 'database',
            'text': f'{len(df):,} records analyzed'
        },
        {
            'icon': 'check-circle',
            'text': 'Dataset processed successfully'
        },
        {
            'icon': 'lightbulb',
            'text': 'Use filters to drill deeper'
        }
    ]

    return JsonResponse({
        'insights': insights
    })