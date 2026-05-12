from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from django.core.mail import EmailMessage
from django.conf import settings
from .models import ScheduledReport
import traceback


def send_scheduled_reports():
    try:
        now = timezone.localtime(timezone.now())
        current_hour = now.hour
        current_minute = now.minute

        reports = ScheduledReport.objects.filter(is_active=True)

        for report in reports:
            try:
                report_hour = report.schedule_time.hour
                report_minute = report.schedule_time.minute

                # Match current time
                if report_hour == current_hour and report_minute == current_minute:

                    recipients = [
                        email.strip()
                        for email in report.recipients.split(',')
                        if email.strip()
                    ]

                    subject = f"Scheduled Dashboard Report - {report.dashboard.name}"

                    html_message = f"""
                    <h2>AI Analytics Platform</h2>

                    <p>Your scheduled dashboard report is ready.</p>

                    <hr>

                    <p><strong>Dashboard:</strong> {report.dashboard.name}</p>

                    <p>
                        <a href="http://127.0.0.1:8000/view/{report.dashboard.id}/">
                            Open Dashboard
                        </a>
                    </p>

                    <br>

                    <p>Generated automatically by AI Analytics Platform.</p>
                    """

                    email = EmailMessage(
                        subject=subject,
                        body=html_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=recipients,
                    )

                    email.content_subtype = "html"

                    email.send(fail_silently=False)

                    report.last_run = now
                    report.save()

                    print(f"Scheduled email sent to {recipients}")

            except Exception as e:
                print("Report Error:", e)
                traceback.print_exc()

    except Exception as e:
        print("Scheduler Error:", e)
        traceback.print_exc()


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_scheduled_reports, 'interval', minutes=1)
    scheduler.start()

    print("APScheduler started...")