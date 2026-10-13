from django.db import migrations, models
from django.db.models import Count, Max, OuterRef, Subquery, Sum
from django.db.models.functions import Coalesce


def remove_duplicate_votes_and_recount(apps, schema_editor):
    """Keep each user's latest vote per model, then recount every score.

    Before this migration a failed vote could change a score without a matching
    vote, so every score is recomputed from the votes that remain.
    """
    Vote = apps.get_model('marketplace', 'Vote')
    SasviewModel = apps.get_model('marketplace', 'SasviewModel')

    duplicates = (Vote.objects.values('user', 'model')
        .annotate(n=Count('id'), keep=Max('id')).filter(n__gt=1))
    for d in duplicates:
        Vote.objects.filter(user=d['user'], model=d['model']).exclude(
            pk=d['keep']).delete()

    total = (Vote.objects.filter(model=OuterRef('pk')).values('model')
        .annotate(total=Sum('value')).values('total'))
    SasviewModel.objects.update(score=Coalesce(Subquery(total), 0))


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0020_auto_20210601_1725'),
    ]

    operations = [
        migrations.RunPython(remove_duplicate_votes_and_recount,
            migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='vote',
            constraint=models.UniqueConstraint(fields=('user', 'model'),
                name='unique_vote_per_user_and_model'),
        ),
    ]
