from django.contrib import admin

from models import Performance


class PerformanceAdmin(admin.ModelAdmin):
    list_display = ("label", "name", "date_create",
                    "duration", "get_duration", "is_valid")
    search_fields = ["name", "label"]

    def is_valid(self, obj):
        return obj.exitcode == 0
    is_valid.boolean = True

admin.site.register(Performance, PerformanceAdmin)
