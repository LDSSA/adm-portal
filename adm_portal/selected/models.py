from django.db import models


class PassedCandidateStatus:
    passed_test = "passed_test"
    drawn = "drawn"
    selected = "selected"
    accepted = "accepted"
    rejected = "rejected"
    not_selected = "not_selected"


class PassedCandidate(models.Model):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE, editable=False)

    status = models.CharField(default=PassedCandidateStatus.passed_test, null=False, max_length=20)

    draw_rank = models.IntegerField(null=True, default=None)
