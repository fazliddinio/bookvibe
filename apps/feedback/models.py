from django.db import models
from django.contrib.auth.models import User


class Feedback(models.Model):
    FEEDBACK_TYPE_CHOICES = [
        ('general', 'General'),
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'),
        ('support', 'Support'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES, default="general")
    message = models.TextField(max_length=500)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="feedback_submissions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_responded = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        db_table = "feedback"

    def __str__(self):
        if self.name:
            return f"Feedback from {self.name} - {self.get_feedback_type_display()}"
        elif self.user:
            return f"Feedback from {self.user.username} - {self.get_feedback_type_display()}"
        else:
            return f"Anonymous feedback - {self.get_feedback_type_display()}"

    def get_short_message(self):
        """Get first 100 characters of message"""
        return self.message[:100] + "..." if len(self.message) > 100 else self.message
