from django.apps import AppConfig


class HotelConfig(AppConfig):
    name = 'hotel'
    verbose_name = 'Messages'

    def ready(self):
        import hotel.signals