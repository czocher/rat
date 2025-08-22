from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from papers.models import Paper
from papers.utils import travers_inferred


@receiver(m2m_changed, sender=Paper.tags.through)
def infer_tags(sender, instance, action, **kwargs):
    if action == "post_add":
        tags = instance.tags.all()
        inferred = set(travers_inferred(tags))
        existing_names = (tag.name for tag in tags)
        inferred_names = (tag.name for tag in inferred)
        if set(inferred_names) == set(existing_names):
            return
        instance.tags.add(*inferred)
