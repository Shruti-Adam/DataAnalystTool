# Data Analyst Tool Using AI

## Overview

**Data Analyst Tool Using AI** is a self-service Business Intelligence and Data Analytics platform that enables users to upload datasets and automatically generate interactive dashboards, statistical reports, and AI-powered insights.

The platform simplifies the data analysis process by combining data visualization, artificial intelligence, automated reporting, and email notification services into a single web application.

---

## Features

### Dataset Analysis

* Upload CSV and Excel datasets
* Automatic data profiling
* Missing value detection
* Duplicate record detection
* Statistical summary generation

### Interactive Dashboard

* KPI Cards
* Bar Charts
* Pie Charts
* Histograms
* Scatter Plots
* Data Tables

### AI-Powered Insights

* Dataset interpretation
* Trend analysis
* Smart recommendations
* Automated summaries
* Business intelligence insights

### Email Notification System

* User verification
* Report sharing
* Email alerts
* Notification delivery using Brevo API

### User Authentication

* User Registration
* Secure Login
* Session Management
* User Profile Management

---

## System Architecture

```text
User
↓
Dataset Upload
↓
Data Processing
↓
Dashboard Generation
↓
AI Insight Generation
↓
Report Generation
↓
Email Notification
```

---

## Technology Stack

### Backend

* Python
* Django

### Data Analytics

* Pandas
* NumPy

### Data Visualization

* Plotly

### Artificial Intelligence

* Hugging Face API

### Email Services

* Brevo API

### Database

* SQLite

### Frontend

* HTML
* CSS
* JavaScript
* Bootstrap

### Deployment

* GitHub
* Render

---

## Project Structure

```text
DataAnalystTool/
│
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│
├── ai_analytics/
│   ├── settings.py
│   ├── urls.py
│
├── api/
│   ├── views.py
│
├── dashboard/
│   ├── views.py
│   ├── ai_insights.py
│
├── templates/
├── static/
├── media/
│
├── manage.py
├── requirements.txt
└── README.md
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/Shruti-Adam/DataAnalystTool.git
cd DataAnalystTool
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / Mac

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file and configure:

```env
SECRET_KEY=your_secret_key

HUGGINGFACE_API_KEY=your_huggingface_api_key

BREVO_API_KEY=your_brevo_api_key

EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_password
```

---

## Run Project

```bash
python manage.py migrate

python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

## Supported Dataset Formats

* CSV
* XLSX (Excel)

---

## AI Capabilities

The system uses Hugging Face models to:

* Generate dataset summaries
* Detect trends
* Produce recommendations
* Provide business insights
* Assist decision making

---

## Email Capabilities

Brevo API is used for:

* Email verification
* Report delivery
* Notification services
* User communication

---

## Deployment

The project is deployed using Render Cloud Platform.

### Deployment Workflow

```text
GitHub → Render → Live Application
```

---

## Academic Project Information

### Project Title

**Data Analyst Tool Using AI**

### Domain

Artificial Intelligence and Data Analytics

### Objective

To automate data analysis, dashboard generation, AI-powered insight creation, and report delivery for users without requiring advanced technical knowledge.

---

## Future Enhancements

* Machine Learning Predictions
* Real-Time Analytics
* Cloud Database Integration
* Mobile Application Support
* Advanced Forecasting Models
* Multi-Language Support
* Automated Report Scheduling

---

## Author

Shruti Adam

### Repository

https://github.com/Shruti-Adam/DataAnalystTool

---

## License

This project is developed for educational and academic purposes.
