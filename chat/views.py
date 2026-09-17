from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import RegisterForm, ProfileForm
from .models import Message, Profile


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'chat/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'chat/login.html', {'error': 'Login yoki parol xato'})
    return render(request, 'chat/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def get_avatar(user):
    try:
        return user.profile.avatar.url
    except Profile.DoesNotExist:
        return '/media/avatars/default.png'


@login_required(login_url='login')
def index(request):
    room_name = 'public'
    messages = Message.objects.filter(room=room_name).order_by('timestamp')[:50]

    for msg in messages:
        try:
            user = User.objects.get(username=msg.username)
            msg.avatar_url = get_avatar(user)
        except User.DoesNotExist:
            msg.avatar_url = '/media/avatars/default.png'

    users = User.objects.exclude(id=request.user.id)

    return render(request, 'chat/index.html', {
        'messages': messages,
        'room_name': room_name,
        'users': users,
        'active': 'group',
    })


@login_required(login_url='login')
def private_chat(request, username):
    other_user = get_object_or_404(User, username=username)

    names = sorted([request.user.username, other_user.username])
    room_name = f'private__{names[0]}__{names[1]}'

    messages = Message.objects.filter(room=room_name).order_by('timestamp')[:50]

    for msg in messages:
        try:
            user = User.objects.get(username=msg.username)
            msg.avatar_url = get_avatar(user)
        except User.DoesNotExist:
            msg.avatar_url = '/media/avatars/default.png'

    users = User.objects.exclude(id=request.user.id)

    return render(request, 'chat/private_chat.html', {
        'messages': messages,
        'room_name': room_name,
        'other_user': other_user,
        'users': users,
        'active': other_user.username,
    })


@login_required(login_url='login')
def profile_view(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'chat/profile.html', {'form': form, 'profile': profile})