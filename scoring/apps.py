from django.apps import AppConfig


class ScoringConfig(AppConfig):
    name = 'scoring'

    # def ready(self):
    #     # Implicitly connect a signal handlers decorated with @receiver.
    #     from . import signals
    #     # Explicitly connect a signal handler.
    #     request_finished.connect(signals.my_pre_enqueue_callback)
    #     request_finished.connect(signals.my_pre_execute_callback)
