from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extra per-user data attached one-to-one to Django's built-in User."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    bio = models.TextField(blank=True, default="")
    avatar_url = models.URLField(blank=True, default="")
    # Medium integration token (kept private; used to cross-post on publish).
    medium_token = models.CharField(max_length=255, blank=True, default="")
    medium_user_id = models.CharField(max_length=64, blank=True, default="")

    def __str__(self):
        return f"Profile({self.user.username})"


@receiver(post_save, sender=User)
def ensure_profile(sender, instance, created, **kwargs):
    """Automatically create a profile whenever a User is created."""
    if created:
        UserProfile.objects.create(user=instance)
