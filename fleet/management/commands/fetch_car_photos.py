from django.core.management.base import BaseCommand

from fleet.photos import fetch_all


class Command(BaseCommand):
    help = "Download three Commons photos for each of the 40 demo cars."

    def handle(self, *args, **options):
        credits, missing = fetch_all(stdout=self.stdout)
        linked = sum(1 for item in credits if item.get("title") or item.get("cached"))
        self.stdout.write(self.style.SUCCESS(f"Photo files ready: {linked}. Missing: {len(missing)}."))
        for item in missing:
            self.stdout.write(self.style.WARNING(f"  {item}"))
