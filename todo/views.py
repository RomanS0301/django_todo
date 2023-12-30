from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404

from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def home(request):
    """
    Домашняя страница
    """
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
        # пользователь ввёл неверные регистрационные данные, то происходит перенапрввление на страницу авторизации
        # с сообщением об ошибке входа
        if user is None:
            return render(request, 'todo/loginuser.html', {'form': AuthenticationForm(),
                                                           'error': 'Имя пользователя или пароль не совпадают'})
        else:
            login(request, user)  # запрет пользователю на посещение админ панели
            # перенапраление пользователя на страницу с текущими задачами
            return redirect('currenttodos')


@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


@login_required
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
            return render(request, 'todo/createtodo.html', {'form': TodoForm(),
                                                            'error': 'Переданы неверные данные'})


@login_required
def currenttodos(request):
    """
    Страница с текущими задачами

    """
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)  # выборка задач по пользователю и не
    # страница с текущими задачами пользователя
    return render(request, 'todo/currenttodos.html', {'todos': todos})


@login_required
def completedtodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'todo/completedtodos.html', {'todos': todos})


@login_required
def viewtodo(request, todo_pk):
    """
    Просмотр, изменение и сохранении задач пользователем
    """
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form, 'error': 'Данные не верны'})


@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')


@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodos')
