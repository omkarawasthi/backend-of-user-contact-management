from django.contrib.auth.models import AbstractUser
from .utils.helper_functions import calculate_age
from django.db import models


# Custom user model
class User(AbstractUser):
    email = models.EmailField(unique=True)
    id = models.AutoField(primary_key=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = "user_table"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# Contact model
class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contacts")
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    aadhar_no = models.CharField(max_length=25, unique=True)
    phone_no = models.CharField(max_length=13,unique=True)
    date_of_birth = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)


    @property
    def age(self):
        if self.date_of_birth:
            return calculate_age(self.date_of_birth)
        return None
    
    class Meta:
        db_table = "contact_table"

    def __str__(self): 
        return f"{self.user.first_name} -> {self.user.last_name}"
    
