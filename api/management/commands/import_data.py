import csv

import django.db.utils
from django.core.management.base import BaseCommand, CommandError

from api.models import Category, Comment, Genre, Review, Title, User

DATA = [
    ['data/category.csv', Category],
    ['data/genre.csv', Genre],
    ['data/titles.csv', Title],
    ['data/genre_title.csv', Title.genre.through],
    ['data/users.csv', User],
    ['data/review.csv', Review],
    ['data/comments.csv', Comment],

]


class Command(BaseCommand):
    help = 'Imports data from csv files to database'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.NOTICE('Please wait until Finished! prompt')
        )
        for datafile, Model in DATA:
            with open(datafile, encoding='utf8') as csvfile:
                reader = csv.DictReader(csvfile)
                try:
                    for row in reader:
                        Model.objects.create(**row)
                    self.stdout.write(
                        self.style.SUCCESS('Successfully created '
                                           f'{Model.__name__} from {datafile}')
                    )
                except django.db.utils.IntegrityError:
                    raise CommandError('Unable to create '
                                       f'{Model.__name__} from {datafile}')
        self.stdout.write(self.style.SUCCESS('Finished!'))
