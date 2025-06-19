from celery import shared_task
from django.conf import settings
from datetime import date,timedelta
from .models import Contact, User
from django.core.mail import send_mail
from .utils.db_logging import delete_old_logs
from datetime import timedelta

@shared_task
def send_upcoming_birthday_reminder():
    tomorrow = date.today() + timedelta(days=1)
    month = tomorrow.month
    day = tomorrow.day

    birthday_contacts = Contact.objects.filter(
        date_of_birth__month=month,
        date_of_birth__day=day,
    )
    count = birthday_contacts.count()

    if count == 0:
        return "No upcoming birthdays."

    full_names = []
    for contact in birthday_contacts:
        name = contact.first_name + " " + contact.last_name
        full_names.append(name)

    names = ", ".join(full_names)
    print("Name :", names)
    
    birthday_user_ids = birthday_contacts.values_list('user_id', flat=True)
    emails_to_notify = list(
        User.objects
            .exclude(id__in=birthday_user_ids)
            .values_list('email', flat=True)
    )
    if not emails_to_notify:
        return "No one to notify."

    subject = "Upcoming Birthday Reminder 🎉"
    message = (
        f"Hello!\n\n"
        f"Just a friendly reminder that tomorrow is the birthday of: {names}.\n"
        "Feel free to send them your warm wishes! 🎂🥳\n\n"
        "Best,\nYour Friendly Bot"
    )

    # from_email = settings.EMAIL_FROM

    send_mail(
        subject=subject,
        message=message,
        from_email='omkar.awasthi@adcuratio.com',
        recipient_list=emails_to_notify,
    )

    return f"Reminder sent to {len(emails_to_notify)} users."


@shared_task
def send_birthday_greetings():
    today = date.today()
    print("today", today)
    birthday_contacts = Contact.objects.filter(
        date_of_birth__month=today.month,
        date_of_birth__day=today.day,
    )

    print("ibirt :",birthday_contacts)
    for contact in birthday_contacts:
        user = contact.user
        print("User email", user.email)
        try:
            send_mail(
                subject="Happy Birthday 🎂",
                message=f"Dear {user.first_name},\n\nWishing you a fantastic birthday filled with joy and love!",
                from_email="omkar.awasthi@adcuratio.com",
                recipient_list=[user.email],
            )
        except Exception as e:
            print(str(e))
    return "Birthday greetings sent."




@shared_task
def scheduled_log_deletion(hours: int = 24):
    try:
        filename, deleted_count = delete_old_logs(hours)

        if deleted_count == 0:
            return {"status":False,"message": f"No logs older than {hours} hours found."}

        return {
            "status":True,
            "message": f"{deleted_count} logs older than {hours} hours backed up and deleted.",
            "backup_file": filename
        }

    except Exception as e:
        return {"status":False,"error": str(e)}