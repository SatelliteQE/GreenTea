from django.contrib import admin
from models import Comment


class CommentAdmin(admin.ModelAdmin):
    list_display = ("username", "created_date", "content", "action")
    readonly_fields = ["job", "recipe", "task"]

admin.site.register(Comment, CommentAdmin)
