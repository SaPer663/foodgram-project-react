import codecs
import csv
import os

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import ForeignKey


def get_fk_model(model, fieldname):
    field_object = model._meta.get_field(fieldname)
    if isinstance(field_object, ForeignKey):
        return field_object.related_model
    return None


def csv_parser(csv_filename):
    with codecs.open(csv_filename, 'r', 'utf_8_sig') as csv_fd:
        reader = csv.reader(csv_fd, delimiter=',')
        for row in reader:
            if row:
                yield row


def insert_data(model, file):
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'data')
    is_header = True
    header = []
    model_instanse = model()
    id = 1
    for row in csv_parser(os.path.join(file_path, file)):
        if is_header:
            header += row
            is_header = False
            continue

        if header[0] != 'id':
            model_instanse.__setattr__('id', id)
            id += 1
        for field, value in zip(header, row):
            rel_model = get_fk_model(model_instanse, field)
            if rel_model is not None:
                model_instanse.__setattr__(field, rel_model(value))
            else:
                model_instanse.__setattr__(field, value)
        model_instanse.save()


class Command(BaseCommand):
    help = """
    Команда для наполнения базы данных из файлов .csv.
    Формат команды: `python manage.py filling *keys`
    `'-a', '--app'` ключ указывает на имя приложения;
    `'-m', '--model'` ключ указывает класс модели в models.py;
    `'-f', '--file'` ключ указывает имя файла в директории `static/data/`
    Пример команды для заполнения данными о пользователях в модели `Title`
    приложения `reviews` из файла `titles.csv`:
    `python manage.py filling -a reviews -m Title -f titles.csv`
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '-a', '--app',
            required=True,
            help='takes the lable of the app')
        parser.add_argument(
            '-m', '--model',
            required=True,
            help='takes the name of the model class')
        parser.add_argument(
            '-f', '--file',
            required=True,
            help='accepts a filename with extension')

    def handle(self, *args, **options):
        try:
            model = apps.get_model(options['app'], options['model'])
            insert_data(model, options['file'])
        except Exception as e:
            raise CommandError(f'{e}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully {model.__name__} filled'
            )
        )
