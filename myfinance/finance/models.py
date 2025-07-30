from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Transition(models.Model):

    Type_Choice = [(
        'income','INCOME'
    ),
    (
        'expense','EXPENSE'
    )
    ]

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    type = models.CharField(max_length=20,choices=Type_Choice)
    amount = models.FloatField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Transition by "+self.user.username+" On "+ str(self.date)