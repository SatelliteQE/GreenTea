import os
from django.conf import settings
from django.core.exceptions import ValidationError

def validator_dir_exists(value):
    print value
    if value.startswith("file://"):
        value = value[7:]
    if not value.startswith("/"):
        value = os.path.join(settings.STORAGE_ROOT, value)
    print value
    if not os.path.isdir(value):
        raise ValidationError("Directory %s doesn't exists" % value)
