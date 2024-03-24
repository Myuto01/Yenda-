from django.apps import AppConfig


class ReservationSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reservation_system'
    
    
    def ready(self):
        import reservation_system.signals