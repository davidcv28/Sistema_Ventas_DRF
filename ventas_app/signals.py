from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Invoice

@receiver(post_save, sender = Invoice)
def new_number_invoicer(sender, instance, created, **kwargs):
    if created:
        new_number = f'FAC-{instance.id:08d}'
        Invoice.objects.filter(pk=instance.pk).update(number_invoice = new_number)
