from django.core.management.base import BaseCommand, CommandError
from activity.models import Activity, Evidence

class Command(BaseCommand):

    help = 'a'

    def handle(self, *args, **options):
        activities = Activity.objects.filter(status=True).values('id', 'type__type_evidence__id', 'type__type_evidence__name')

        for activity in activities:
            evidence = Evidence(activity_id=activity['id'], type_evidence_id=activity['type__type_evidence__id'])
            try:
                evidence.full_clean()
            except:
                print('%s --%s --%s' % (activity['id'], activity['type__type_evidence__id'], activity['type__type_evidence__name']))
            evidence.save()
        self.stdout.write("Evidencias")