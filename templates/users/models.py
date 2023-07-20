from django.db import models
from uuid import uuid4

class EmailConfirmationToken(models.Model):
    email = models.EmailField()
    token = models.UUIDField(default=uuid4)