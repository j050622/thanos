from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class ThanosConfig(AppConfig):
    name = 'thanos'

    def ready(self):
        autodiscover_modules('thanos')
