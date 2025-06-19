from datetime import date, timedelta
from dotenv import load_dotenv


load_dotenv()

# function to calculate age
def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


# find birthday of users in next seven days.
def find_birthday_next_week(days):
    from user.models import Contact


    upcoming = []
    today = date.today()

    # Use select_related to fetch User alongside Contact for efficiency
    for offset in range(days):
        target_date = today + timedelta(days=offset)
        contacts = (Contact.objects
                    .select_related('user')
                    .filter(
                        date_of_birth__month=target_date.month,
                        date_of_birth__day=target_date.day,
                    ))

        for contact in contacts:
            # Safely retrieve email from related User
            email = getattr(contact, 'user', None) and contact.user.email
            upcoming.append({
                "id": contact.id,
                "first_name": f"{contact.first_name}",
                "last_name": f"{contact.last_name}",
                "email": email,
                "phone_no":contact.phone_no,
                "dob": contact.date_of_birth,
            })

    return upcoming