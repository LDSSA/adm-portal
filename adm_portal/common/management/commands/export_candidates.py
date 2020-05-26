import csv

from django.core.management.base import BaseCommand

from staff.export import get_all_candidates


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:
        data = get_all_candidates()
        with open("candidates.csv", "w", newline="") as csvfile:
            w = csv.DictWriter(csvfile, data.headers, lineterminator="\n")
            w.writeheader()
            w.writerows(data.rows)

        self.stdout.write(self.style.SUCCESS("Done"))
