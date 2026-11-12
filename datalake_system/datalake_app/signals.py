from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import AWSConfig

@receiver(post_save, sender=User)
def create_aws_config(sender, instance, created, **kwargs):
    """Create AWS config for new users"""
    if created:
        AWSConfig.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_aws_config(sender, instance, **kwargs):
    """Save AWS config when user is saved"""
    try:
        instance.aws_config.save()
    except AWSConfig.DoesNotExist:
        AWSConfig.objects.create(user=instance)