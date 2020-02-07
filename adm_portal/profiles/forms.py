from django.forms import ModelForm

from .models import Profile


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ["full_name", "profession", "gender", "ticket_type"]
