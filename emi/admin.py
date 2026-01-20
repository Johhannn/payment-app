from django.contrib import admin
from .models import User, EMISchedule, Payment, Rule

# Register your models here.

admin.site.register(User)
admin.site.register(EMISchedule)
admin.site.register(Payment)
admin.site.register(Rule)