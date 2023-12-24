from django.db import models
from django.contrib.auth.models import User


class Todo(models.Model):
    title = models.CharField(max_length=150, verbose_name='Заголовок')
    task = models.TextField(blank=True, verbose_name='Задача')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания задачи') # Дата и время создания задачи
    datecompleted = models.DateTimeField(null=True, blank=True, verbose_name='Дата и время завершения задачи')  # Завершение задачи
    important = models.BooleanField(default=False, verbose_name='ВАЖНАЯ ЗАДАЧА')  # Отметка о важности задачи, по умолчанию отсутствует
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

