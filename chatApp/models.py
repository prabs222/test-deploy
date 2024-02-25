from django.db import models
from django.db.models import Q
from accountApp.models import User
from twamitraApp.models import CorporateAppointment, CorporateDB

class ThreadManager(models.Manager):
    def by_user(self, **kwargs):
        user = kwargs.get('user')
        lookup = Q(customer=user,is_active = True) | Q(corporate=user,is_active = True)
        qs = self.get_queryset().filter(lookup).order_by('created_at').distinct()
        return qs


class Thread(models.Model):
    appointment = models.ForeignKey(CorporateAppointment, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="corporateThreads")
    corporate = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ThreadManager()
       
    def __str__(self):
        return f"Thread-{self.id}"

class ChatMessage(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} - {self.message} - {self.timestamp}"

    class Meta:
        ordering = ['timestamp']