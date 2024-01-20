import csv
import sqlite3

from django.core.management import BaseCommand

from api_yamdb.settings import BASE_DIR
from reviews.models import (Category, Comments, Genre, Review,
                            Title, User)


def import_csv():

    with open(
            f'{BASE_DIR}/static/data/users.csv', encoding='utf-8'
    ) as csv_file:
        file_reader = csv.DictReader(csv_file, delimiter=',')
        for row in file_reader:
            User.objects.update_or_create(
                id=row["id"],
                username=row["username"],
                email=row["email"],
                role=row["role"],
                bio=row["bio"],
                first_name=row["first_name"],
                last_name=row["last_name"]
            )

    with open(
            f'{BASE_DIR}/static/data/category.csv', encoding='utf-8'
    ) as csv_file:
        file_reader = csv.DictReader(csv_file, delimiter=',')
        for row in file_reader:
            Category.objects.update_or_create(
                id=row["id"],
                name=row["name"],
                slug=row["slug"],
            )

    with open(
        f'{BASE_DIR}/static/data/genre.csv', encoding='utf-8'
    ) as csv_file:
        file_reader = csv.DictReader(csv_file, delimiter=',')
        for row in file_reader:
            Genre.objects.update_or_create(
                id=row["id"],
                name=row["name"],
                slug=row["slug"],
            )

    with open(
        f'{BASE_DIR}/static/data/titles.csv', encoding='utf-8'
    ) as csv_file:
        file_reader = csv.DictReader(csv_file, delimiter=',')
        for row in file_reader:
            Title.objects.update_or_create(
                id=row['id'],
                name=row['name'],
                year=row['year'],
                category_id=row['category']
            )

    with open(
        f'{BASE_DIR}/static/data/review.csv', encoding='utf-8'
    ) as csv_file:
        file_reader = csv.DictReader(csv_file, delimiter=',')
        for row in file_reader:
            author = User.objects.get(id=row["author"])
            Review.objects.update_or_create(
                id=row['id'],
                title_id=row['title_id'],
                text=row['text'],
                author_id=author.id,
                score=row['score'],
                pub_date=row['pub_date']
            )

    with open(
        f'{BASE_DIR}/static/data/comments.csv', encoding='utf-8'
    ) as csv_file:
        file_reader = csv.DictReader(csv_file, delimiter=',')
        for row in file_reader:
            author = User.objects.get(id=row["author"])
            Comments.objects.update_or_create(
                id=row['id'],
                review_id=row['review_id'],
                text=row['text'],
                author_id=author.id,
                pub_date=row['pub_date']
            )

    # Отдельное заполнение таблицы reviews_title_genre
    # (при отсутствии соответствующей модели в models.py):
    db_path = 'db.sqlite3'
    db_connector = sqlite3.connect(db_path)
    db_cursor = db_connector.cursor()

    with open(f'{BASE_DIR}/static/data/genre_title.csv',
              'r', encoding='utf-8') as csv_file:
        file_reader = csv.DictReader(csv_file, delimiter=',')
        file_rows = [(column['id'],
                      column['title_id'],
                      column['genre_id']) for column in file_reader]

    db_cursor.executemany(
        "INSERT INTO reviews_title_genre"
        "(id, title_id, genre_id)"
        "VALUES (?, ?, ?);", file_rows)
    db_connector.commit()


class Command(BaseCommand):
    help = ('Загрузка данных из csv-файлов:'
            'python manage.py test_data_db')

    def handle(self, *args, **kwargs):
        import_csv()


if __name__ == '__main__':
    print('Запуск: python manage.py test_data_db')
