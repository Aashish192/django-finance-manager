from django.contrib import admin
from .models import Transition

class TransitionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'type', 'amount', 'date']  # columns shown in admin list view
    list_filter = ['type', 'date']  # filters sidebar
    search_fields = ['user__username', 'description']  # search box

admin.site.register(Transition, TransitionAdmin)
