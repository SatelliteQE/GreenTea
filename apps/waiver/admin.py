from django.contrib import admin

from models import Comment


class CommentAdmin(admin.ModelAdmin):
    list_display = ("username", "created_date", "content", "action",)
    raw_id_fields = ("test", )
    readonly_fields = ["job", "recipe", "task"]
    fieldsets = (
        (None, {
            'fields': ('action', 'username', 'content', 'test', ('job', 'recipe', 'task'))
        }),
    )
admin.site.register(Comment, CommentAdmin)
