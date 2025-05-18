from django.core.management.base import BaseCommand

from sms.models import SMSTariff


class Command(BaseCommand):
    help = "SMS tariflarini bazaga yuklaydi."

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Eski tariflarni o‘chirib tashlaydi va yangidan yuklaydi.'
        )

    def handle(self, *args, **options):
        tariffs = [
            {"name": "Student Paket", "sms_count": 100, "price": 3000, "price_per_sms": 30.0},
            {"name": "Starter Paket", "sms_count": 100, "price": 4500, "price_per_sms": 45.0},
            {"name": "Mini Paket", "sms_count": 300, "price": 12000, "price_per_sms": 40.0},
            {"name": "Standart Paket", "sms_count": 1000, "price": 38000, "price_per_sms": 38.0},
            {"name": "Pro Paket", "sms_count": 5000, "price": 180000, "price_per_sms": 36.0},
        ]

        if options['force']:
            SMSTariff.objects.all().delete()
            self.stdout.write(self.style.WARNING('Barcha eski tariflar o‘chirildi.'))

        created = 0
        for tariff_data in tariffs:
            tariff, is_created = SMSTariff.objects.get_or_create(
                name=tariff_data["name"],
                defaults={
                    "sms_count": tariff_data["sms_count"],
                    "price": tariff_data["price"],
                    "price_per_sms": tariff_data["price_per_sms"],
                }
            )
            if is_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"{created} ta tarif yaratildi."))
