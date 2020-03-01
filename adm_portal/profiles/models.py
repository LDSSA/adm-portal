from django.db import models

gender_choices = [("f", "Female"), ("m", "Male"), ("other", "Other/Prefer not to say")]
ticket_types_choices = [("student", "Student"), ("regular", "Regular"), ("company", "Company")]


# todo: add more fields, this model is incomplete, add NIF
class Profile(models.Model):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)

    full_name = models.CharField(blank=False, null=False, max_length=100)

    profession = models.CharField(blank=False, null=False, max_length=50)

    gender = models.CharField(blank=False, null=False, choices=gender_choices, max_length=10)

    ticket_type = models.CharField(blank=False, null=False, choices=ticket_types_choices, max_length=15)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_student(self) -> bool:
        return self.ticket_type == "student"
