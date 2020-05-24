from django.db import models


class ProfileGenders:
    female = "Female"
    male = "Male"
    other = "Other/Prefer not to say"


class ProfileTicketTypes:
    student = "Student"
    regular = "Regular"
    company = "Company"
    scholarship = "Scholarship"


class Profile(models.Model):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)

    full_name = models.CharField(null=False, max_length=100)

    profession = models.CharField(null=False, max_length=50)

    gender = models.CharField(null=False, max_length=25)

    ticket_type = models.CharField(null=False, max_length=25)

    company = models.CharField(null=False, default="", max_length=40)

    id_card_location = models.CharField(null=True, default=None, max_length=200)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
