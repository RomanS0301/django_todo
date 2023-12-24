from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm


def home(request):
    return render(request, 'todo/home.html')


def signupuser(request):
    """
    Создание нового пользователя, проверка на совпадение паролей, проверка на уникальность пользователя, запрет на
    посещение пользователем админ панели, перенаправление пользователя на страницу с текущими задачами
    """
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:  # проверка на совпадение паролей
            # перехват ошибки на существующего пользователя
            try:
                user = User.objects.create_user(request.POST['username'],
                                                password=request.POST['password1'])  # создание нового пользователя
                user.save()  # сохранение нового пользователя
                login(request, user)  # запрет пользователю на посещение админ панели
                # перенапраление пользователя на страницу с текущими задачами
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, 'todo/signupuser.html', {'form': UserCreationForm(),
                                                                'error': 'Такое имя пользователя уже существует'})
        else:
            # сообщить пользователю о несовпадении паролей,перенаправить его на страницу регистрации
            return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'Пароли не совпадают'})


def loginuser(request):
    """
    Вход пользователя в личный кабинет, проверка на совпадение регистрационных данных,перенаправление на страницу
    """
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/loginuser.html', {'form': AuthenticationForm(),
                                                           'error': 'Имя пользователя или пароль не совпадают'})
        else:
            login(request, user)  # запрет пользователю на посещение админ панели
            # перенапраление пользователя на страницу с текущими задачами
            return redirect('currenttodos')


def logoutuser(request):
    """
    Выход пользователя из личного кабинета

    """
    if request.method == 'POST':
        logout(request)
        return redirect('home')


def createtodo(request):
    """
    Создание новой задачи с личной страницы пользователя. Сохранение задачи в базу данных Перехват ошибки ValueError
    """
    if request.method == 'GET':
        return render(request, 'todo/createtodo.html', {'form': TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtask = form.save(commit=False)
            newtask.user = request.user
            newtask.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/currenttodos.html', {'form': TodoForm(),
                                                              'error': 'Переданы неверные данные'})


def currenttodos(request):
    """
    Страница с текущими задачами

    """
    return render(request, 'todo/currenttodos.html')
