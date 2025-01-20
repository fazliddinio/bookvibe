from django.core.management.base import BaseCommand
from apps.books.models import Genre


class Command(BaseCommand):
    help = "Add 5 new genres to the database"

    def handle(self, *args, **options):
        new_genres = [
            {
                "name": "Mystery",
                "description": "Books featuring puzzles, crimes, and investigations that need to be solved.",
                "color": "#8B4513",
            },
            {
                "name": "Science Fiction",
                "description": "Futuristic stories exploring scientific concepts, space, and technology.",
                "color": "#4169E1",
            },
            {
                "name": "Biography",
                "description": "Non-fiction accounts of real people's lives and experiences.",
                "color": "#4682B4",  # Steel blue instead of red
            },
            {
                "name": "Poetry",
                "description": "Literary works written in verse form, expressing emotions and ideas.",
                "color": "#9370DB",
            },
            {
                "name": "Self-Help",
                "description": "Books designed to help readers improve their personal development and life skills.",
                "color": "#32CD32",
            },
        ]

        created_count = 0
        for genre_data in new_genres:
            genre, created = Genre.objects.get_or_create(
                name=genre_data["name"],
                defaults={
                    "description": genre_data["description"],
                    "color": genre_data["color"],
                },
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully created genre: {genre.name}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Genre already exists: {genre.name}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"Successfully added {created_count} new genres!")
        )
