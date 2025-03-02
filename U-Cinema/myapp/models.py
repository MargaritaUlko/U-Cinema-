from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from shutil import copyfile
from django.db.models.signals import post_save
from django.dispatch import receiver
from googletrans import Translator
import requests
from django.contrib.auth.hashers import make_password
import logging
from django.utils.translation import gettext_lazy as _
logger = logging.getLogger(__name__)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('admin', 'Администратор'),
    ]
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='user')
    def save(self, *args, **kwargs):
        if not self.password.startswith('argon2$'):  # Проверяем, не зашифрован ли уже пароль
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

# TODO: Реализовать комментарии и высчитывание оценок критиков и пользователей

class Movie(models.Model):
    title = models.CharField(_('Название'), max_length=100)
    description = models.TextField(_('Описание'), null=True, blank=True)
    poster = models.ImageField(_('Постер'), upload_to='movie_posters', null=True, blank=True)
    year = models.IntegerField(_('Год'), null=True, blank=True)
    country = models.CharField(_('Страна'), max_length=100, null=True, blank=True)
    genre = models.CharField(_('Жанр'), max_length=100, null=True, blank=True)
    director = models.CharField(_('Режиссер'), max_length=100, null=True, blank=True)
    screenplay = models.CharField(_('Сценарист'), max_length=100, null=True, blank=True)
    producer = models.CharField(_('Продюсер'), max_length=100, null=True, blank=True)
    cinematography = models.CharField(_('Оператор'), max_length=100, null=True, blank=True)
    composer = models.CharField(_('Композитор'), max_length=100, null=True, blank=True)
    production_designer = models.CharField(_('Художник по постановке'), max_length=100, null=True, blank=True)
    editor = models.CharField(_('Монтажер'), max_length=100, null=True, blank=True)
    budget = models.DecimalField(_('Бюджет'), max_digits=12, decimal_places=2, null=True, blank=True)
    class Meta:
        verbose_name = _("Фильм")
        verbose_name_plural = _("Фильмы")
    def __str__(self):
        return self.title

class Hall(models.Model):
    name = models.CharField("Название зала", max_length=255)
    row_number = models.IntegerField("Количество рядов", default=5)
    seats_per_row = models.IntegerField("Мест в ряду", default=10)
    seating_plan = models.JSONField("Схема мест", blank=True, default=dict)  # Оставляем пустым, чтобы заполнилось в save()
    capacity = models.PositiveIntegerField("Вместимость", editable=False, default=0)

    def save(self, *args, **kwargs):
        # Если схема не задана, заполняем её по умолчанию
        if not self.seating_plan:
            self.seating_plan = {str(i): [1] * self.seats_per_row for i in range(1, self.row_number + 1)}



        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.capacity} мест)"

    class Meta:
        verbose_name = _("Зал")
        verbose_name_plural = _("Залы")

class Session(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("Фильм"))
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("Зал"))
    start_datetime = models.DateTimeField(_('Время начала'))
    ticket_price = models.DecimalField(_('Цена билета'), max_digits=10, decimal_places=2)
    def __str__(self):
        return f"{self.movie.title} - {self.start_datetime.strftime('%Y-%m-%d %H:%M')}"
    class Meta:
        verbose_name = _("Сеанс")
        verbose_name_plural = _("Сеансы")




class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    STATUS_CHOICES = [
        ('purchased', 'Куплен'),
        ('canceled', 'Отменен'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    row_number = models.IntegerField()
    seat_number = models.IntegerField()
    ticket_count = models.IntegerField(default = 1)
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    rating = models.IntegerField()


@receiver(post_save, sender=Booking)
def increment_ticket_count(sender, instance, created, **kwargs):
    if created:  # Проверяем, создана ли новая запись
        instance.ticket_count += 1  # Увеличиваем значение ticket_count на 1
        instance.save()  # Сохраняем изменения в объекте Session

@receiver(post_save, sender=Movie)
def fetch_movie_data(sender, instance, **kwargs):
    """Функция скачивает постер, год и описание фильма, если они не были заданы вручную."""
    translator = Translator()
    translated_title = translator.translate(instance.title, src='ru', dest='en').text

    logger.info(f"Запрос к API OMDB для фильма: {translated_title}")

    api_key = 'fd625bb4'  # Здесь укажи свой API-ключ от OMDB
    url = f"https://www.omdbapi.com/?t={translated_title}&apikey={api_key}"
    logger.info(f"URL запроса: {url}")

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        logger.info(f"Ответ от API: {data}")  

        poster_url = data.get("Poster")
        year = data.get("Year")
        description = data.get("Plot")

        if description and description != "N/A":
            translated_description = translator.translate(description, src='en', dest='ru').text
        else:
            translated_description = None

        updated = False
        if year and not instance.year:
            instance.year = int(year)
            updated = True

        if translated_description and not instance.description:
            instance.description = translated_description
            updated = True

        if poster_url and poster_url != "N/A" and not instance.poster:
            logger.info(f"Скачивание постера с URL: {poster_url}")
            image_response = requests.get(poster_url)
            if image_response.status_code == 200:
                file_name = f"{instance.title.replace(' ', '_')}.jpg"
                instance.poster.save(file_name, ContentFile(image_response.content))
                updated = True
            else:
                logger.error(f"Ошибка при скачивании изображения: {image_response.status_code}")

        # Если были обновления, сохраняем объект
        if updated:
            instance.save()
            logger.info(f"Данные фильма {instance.title} обновлены.")

    else:
        logger.error(f"Ошибка при запросе к API: {response.status_code}, Ответ: {response.text}")
