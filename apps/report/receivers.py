
import json
import logging
from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.models import EnumResult, Task
from models import Score
from django.core.exceptions import MultipleObjectsReturned

logger = logging.getLogger("main")


@receiver(post_save, sender=Task)
def recount_test_score(sender, **kwargs):
    task = kwargs["instance"]
    if not task.recipe.job.schedule:
        return
    results = Task.objects.filter(test=task.test,
                                  recipe__job__schedule=task.recipe.job.schedule)\
        .values("result")\
        .annotate(count=Count('result')).order_by("result")

    try:
        score, created = Score.objects.get_or_create(
            test=task.test, schedule=task.recipe.job.schedule)
    except MultipleObjectsReturned:
        logger.error(
            "Exist so many records - test: %d, schedule: %s" %
            (task.test.id, task.recipe.job.schedule))
        return

    # count score
    score.score = 0
    score.count = 0
    for it in results:
        score.count += it["count"]
        if EnumResult.FAIL == it["result"]:
            score.score -= 2 * it["count"]
        elif EnumResult.WARN == it["result"]:
            score.score -= 1 * it["count"]
        elif EnumResult.PASS == it["result"]:
            score.score += 0 * it["count"]

    score.rate = (score.score / float(score.count))
    score.result = json.dumps(list(results))
    score.save()
