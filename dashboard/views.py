# dashboard/views.py

import os
import pandas as pd
import numpy as np
from io import StringIO
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone
from .models import Dataset, Dashboard
import shutil
import uuid
import threading

# ============================================================
# DETECT DATASET TYPE
# ============================================================

def detect_dataset_type(df):

    columns_text = ' '.join(df.columns.astype(str).str.lower())

    if any(word in columns_text for word in ['salary', 'job', 'experience', 'position', 'company']):
        return {
            'type': 'job_salary',
            'title': 'Job & Salary Analytics',
            'group_by': ['job_title', 'company', 'location', 'industry'],
            'numeric_cols': ['salary', 'years_experience', 'age'],
            'chart_title': 'Salary Analysis by Position'
        }

    elif any(word in columns_text for word in ['sales', 'revenue', 'profit', 'customer', 'order']):
        return {
            'type': 'sales',
            'title': 'Sales & Revenue Analytics',
            'group_by': ['region', 'product', 'category'],
            'numeric_cols': ['sales', 'revenue', 'quantity', 'profit'],
            'chart_title': 'Sales Performance Analysis'
        }

    elif any(word in columns_text for word in ['employee', 'department', 'attrition', 'tenure']):
        return {
            'type': 'hr',
            'title': 'HR Analytics Dashboard',
            'group_by': ['department', 'position', 'location'],
            'numeric_cols': ['salary', 'years', 'age', 'performance_score'],
            'chart_title': 'Department Performance'
        }

    elif any(word in columns_text for word in ['student', 'grade', 'score', 'exam', 'attendance']):
        return {
            'type': 'education',
            'title': 'Education Analytics Dashboard',
            'group_by': ['grade', 'subject', 'gender'],
            'numeric_cols': ['score', 'marks', 'attendance', 'percentage'],
            'chart_title': 'Academic Performance'
        }

    else:

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

        return {
            'type': 'custom',
            'title': 'Data Analytics Dashboard',
            'group_by': categorical_cols[:4] if categorical_cols else [],
            'numeric_cols': numeric_cols[:5] if numeric_cols else [],
            'chart_title': 'Data Analysis'
        }

# ============================================================
# DASHBOARD HOME
# ============================================================

@login_required
def index_view(request):

    dashboards = Dashboard.objects.filter(user=request.user)

    total_records = sum([d.dataset.row_count for d in dashboards]) if dashboards else 0
    total_charts = len(dashboards) * 4
    total_insights = len(dashboards) * 5

    context = {
        'dashboards': dashboards,
        'total_records': total_records,
        'total_charts': total_charts,
        'total_insights': total_insights,
    }

    return render(request, 'dashboard/index.html', context)

# ============================================================
# CREATE DASHBOARD
# ============================================================

@login_required
def create_view(request):

    if request.method == 'POST':

        uploaded_file = request.FILES.get('dataset')

        if uploaded_file:

            os.makedirs('media/datasets/', exist_ok=True)

            fs = FileSystemStorage(location='media/datasets/')
            filename = fs.save(uploaded_file.name, uploaded_file)

            file_path = fs.path(filename)

            try:

                # ====================================================
                # LOAD SMALLER DATASET FOR PERFORMANCE
                # ====================================================

                if filename.endswith('.csv'):

                    df = pd.read_csv(
                        file_path,
                        encoding='utf-8',
                        nrows=3000,
                        low_memory=False
                    )

                elif filename.endswith(('.xlsx', '.xls')):

                    df = pd.read_excel(
                        file_path,
                        nrows=3000
                    )

                else:

                    messages.error(request, 'Unsupported file format')
                    return redirect('dashboard:create')

                # ====================================================
                # CLEAN COLUMNS
                # ====================================================

                df.columns = (
                    df.columns
                    .str.strip()
                    .str.lower()
                    .str.replace(' ', '_')
                )

                dataset_info = detect_dataset_type(df)

                # ====================================================
                # SAVE DATASET
                # ====================================================

                dataset = Dataset.objects.create(
                    user=request.user,
                    name=uploaded_file.name,
                    file=f'datasets/{filename}',
                    file_type=filename.split('.')[-1],
                    row_count=len(df),
                    column_count=len(df.columns)
                )

                dashboard = Dashboard.objects.create(
                    user=request.user,
                    dataset=dataset,
                    name=f"{dataset_info['title']} - {uploaded_file.name}",
                    dashboard_type=dataset_info['type'],
                    theme=request.POST.get('theme', 'corporate'),
                    config={'dataset_info': dataset_info}
                )

                # ====================================================
                # STORE TEMP DATA
                # ====================================================

                request.session['temp_dataframe'] = df.to_json()
                request.session['dataset_info'] = dataset_info

                messages.success(request, 'Dashboard created successfully!')

                return redirect('dashboard:view', dashboard_id=dashboard.id)

            except Exception as e:

                messages.error(request, f'Error: {str(e)}')

                if os.path.exists(file_path):
                    os.remove(file_path)

                return redirect('dashboard:create')

    return render(request, 'dashboard/create.html')

# ============================================================
# VIEW DASHBOARD
# ============================================================

@login_required
def view_dashboard(request, dashboard_id):

    try:

        dashboard = Dashboard.objects.get(
            id=dashboard_id,
            user=request.user
        )

    except Dashboard.DoesNotExist:

        messages.error(request, 'Dashboard not found')
        return redirect('dashboard:index')

    # ========================================================
    # CACHE
    # ========================================================

    cache_key = f'dashboard_df_{dashboard_id}_{request.user.id}'

    df = cache.get(cache_key)

    if df is None:

        df_json = request.session.get('temp_dataframe')

        if df_json:

            df = pd.read_json(StringIO(df_json))

        else:

            file_path = dashboard.dataset.file.path

            if not os.path.exists(file_path):

                messages.error(request, 'Dataset file not found')
                return redirect('dashboard:index')

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

        cache.set(cache_key, df, timeout=600)

    dataset_info = request.session.get(
        'dataset_info',
        detect_dataset_type(df)
    )

    # ========================================================
    # SAMPLE TABLE
    # ========================================================

    sample_data = df.head(10).to_html(
        classes='table table-striped table-hover',
        index=False,
        escape=False
    )

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # ========================================================
    # KPIs
    # ========================================================

    kpis = [
        {
            'value': f'{len(df):,}',
            'label': 'Total Records',
            'trend': '+'
        },
        {
            'value': len(df.columns),
            'label': 'Total Columns',
            'trend': '='
        },
        {
            'value': len(numeric_cols),
            'label': 'Numeric Fields',
            'trend': '+'
        },
    ]

    context = {
        'dashboard': dashboard,
        'dataset_info': dataset_info,
        'sample_data': sample_data,
        'kpis': kpis,
        'row_count': len(df),
        'col_count': len(df.columns),
        'dashboard_id': dashboard.id
    }

    return render(request, 'dashboard/view.html', context)

# ============================================================
# DELETE DASHBOARD
# ============================================================

@login_required
@require_http_methods(["POST"])
def delete_dashboard(request, dashboard_id):

    try:

        dashboard = Dashboard.objects.get(
            id=dashboard_id,
            user=request.user
        )

        dashboard_name = dashboard.name
        dataset = dashboard.dataset

        dashboard.delete()

        cache_key = f'dashboard_df_{dashboard_id}_{request.user.id}'
        cache.delete(cache_key)

        if not Dashboard.objects.filter(dataset=dataset).exists():

            if dataset.file and os.path.exists(dataset.file.path):

                try:
                    os.remove(dataset.file.path)
                except:
                    pass

            dataset.delete()

        return JsonResponse({
            'status': 'success',
            'message': f'Dashboard "{dashboard_name}" deleted successfully'
        })

    except Dashboard.DoesNotExist:

        return JsonResponse({
            'status': 'error',
            'message': 'Dashboard not found'
        }, status=404)

    except Exception as e:

        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

# ============================================================
# DUPLICATE DASHBOARD
# ============================================================

@login_required
@require_http_methods(["POST"])
def duplicate_dashboard(request, dashboard_id):

    try:

        original = Dashboard.objects.get(
            id=dashboard_id,
            user=request.user
        )

        original_dataset = original.dataset

        file_extension = original_dataset.file.name.split('.')[-1]

        new_filename = f"{uuid.uuid4().hex}.{file_extension}"

        new_file_path = f"datasets/{new_filename}"

        os.makedirs('media/datasets/', exist_ok=True)

        source_path = original_dataset.file.path
        dest_path = f"media/{new_file_path}"

        if os.path.exists(source_path):

            shutil.copy2(source_path, dest_path)

        new_dataset = Dataset.objects.create(
            user=request.user,
            name=f"Copy of {original_dataset.name}",
            file=new_file_path,
            file_type=original_dataset.file_type,
            row_count=original_dataset.row_count,
            column_count=original_dataset.column_count
        )

        new_dashboard = Dashboard.objects.create(
            user=request.user,
            dataset=new_dataset,
            name=f"Copy of {original.name}",
            dashboard_type=original.dashboard_type,
            theme=original.theme,
            config=original.config
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Dashboard duplicated successfully',
            'dashboard_id': new_dashboard.id
        })

    except Exception as e:

        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

# ============================================================
# SEND EMAIL ASYNC
# ============================================================

def send_email_async(subject, message, recipient_list,
                     dashboard_name=None, dashboard_id=None):

    def send():

        try:

            html_message = f"""
            <h2>AI Analytics Dashboard</h2>

            <p>{message}</p>

            <p>
                <strong>Dashboard:</strong>
                {dashboard_name}
            </p>

            <p>
                View Dashboard:
                <a href="https://dataanalysttool.onrender.com/dashboard/view/{dashboard_id}/">
                    Open Dashboard
                </a>
            </p>
            """

            email = EmailMessage(
                subject=subject,
                body=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=recipient_list,
            )

            email.content_subtype = "html"

            email.send(fail_silently=False)

        except Exception as e:

            print("EMAIL ERROR:", e)

    thread = threading.Thread(target=send)
    thread.start()