from django.contrib import admin
from .models import RetrivConfig

    
@admin.register(RetrivConfig)
class RetrivConfigAdmin(admin.ModelAdmin):
    list_display = ["k", "search_type", "score_threshold", "fetch_k", "lambda_mult"]
    
    readonly_fields = ()