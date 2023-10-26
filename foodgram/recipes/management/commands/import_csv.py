from django.core.management import BaseCommand
from pathlib import Path
from csv import DictReader

from recipes.models import Ingredient


def import_csv():
    file = f'{Path(__file__).parent.parent.parent.parent}/data/ingredients.csv'

    for item in DictReader(open(file, encoding='utf-8')):
        data = Ingredient(
            name=item['name'],
            measurement_unit=item['measurement_unit']
        )
        data.save()
    print('завершена успешно.\n\n'
          '================================================'
          '\n')


class Command(BaseCommand):

    def handle(self, *args, **options):
        import_csv()
