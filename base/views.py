from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from .models import Room, Topic, Message
from .forms import RoomForm

# Create your views here.
# Las views son las request (querys) del cliente

"""rooms = [

    {'id':1, 'name':"Let's Learn Pyton!"},
    {'id':2, 'name':"Design With Me"},
    {'id':3, 'name':"Frontend Developers"},

]"""


def loginPage(request):

    page = 'login' #para el if else de login_register

    if request.user.is_authenticated:

        return redirect('home')

    if request.method=="POST":

        username=request.POST.get('username').lower()
        password=request.POST.get('password')

        try:
            user=User.objects.get(username=username)

        except:
            messages.error(request, "User doesn't exist!")
            

        user = authenticate(request, username=username, password=password) #da error o un objecto de user que coincida

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or Password do not match!')


    context = {'page' : page}

    return render(request, 'base/login_register.html', context)


def logoutUser(request):

    logout(request)
    return redirect('home')


def registerUser(request):

    form = UserCreationForm()

    context = {'form' : form} #pasa el string para que lo reconozca el html

    if request.method == 'POST':

        form = UserCreationForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)#el commit false es para que retorne el usuario y limpiar la data

            user.username = user.username.lower()

            user.save()

            login(request, user)

            return redirect('home')

        else:

            messages.error(request, 'An error occurred during registration.')

    return render(request, 'base/login_register.html', context)


def home(request):

    q = request.GET.get('q') if request.GET.get('q') != None else''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | #or
        Q(name__icontains=q) |
        Q(description__icontains=q)
        ) #el doble __ es para que el query vaya del padre al hijo
    topics = Topic.objects.all()
    room_count=rooms.count()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)) #filtra el lado izquierdo por el content del derecho
    context = {'rooms':rooms, 'topics':topics, 'room_count':room_count, 'room_messages':room_messages}
    return render(request, "base/home.html", context) 

def room(request, pk):

    room = Room.objects.get(id=pk)

    room_messages = room.message_set.all()
    #el nombre de padre.children ambos en minus, basicamente que nos de todos los child del parent
    room_participants = room.participants.all()
    #al ser many to many se puede usar el metodo .all

    if request.method == 'POST':

        message = Message.objects.create(

            user = request.user,
            room = room,
            body = request.POST.get('body')#pasado con el name del html

        )    
        room.participants.add(request.user)
        return redirect('room', pk=room.id) #refreshea pasando el parametro del id
   
    context = {'room':room, 'room_messages' : room_messages, 'participants' : room_participants}

    return render(request, "base/room.html", context)

def userProfile(request, pk):

    user = User.objects.get(id=pk)

    rooms = user.room_set.all()

    room_messages = user.message_set.all()

    topics = Topic.objects.all()

    context = {'user' : user, 'rooms' : rooms, 'room_messages':room_messages, 'topics':topics}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def create_room(request):
    form = RoomForm()
    if request.method=='POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False) 
            #como el host no tiene que pasarse por form, esto es para 
            #que lo tome desde la request y lo guarde solo
            room.host = request.user
            room.save()
            return redirect('home')

    context={'form':form}
    return render(request, "base/room_form.html", context)

@login_required(login_url='login')   
def update_room(request, pk):
    room = Room.objects.get(id=pk)#siempre se usa el objects cuando queryas un model
    form = RoomForm(instance=room)

    if request.user != room.host: #si no sos el creador del room no podes updatear

        return HttpResponse('You are not allowed here')

    if request.method=='POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
            
    context={'form':form}
    return render(request, "base/room_form.html", context)

@login_required(login_url='login')
def delete_room(request, pk):

    room = Room.objects.get(id=pk)

    if request.user != room.host: #si no sos el creador del room no podes updatear

        return HttpResponse('You are not allowed here')
    
    if request.method=='POST':
        room.delete()
        return redirect('home')
        
    return render(request, 'base/delete.html', {'obj':room})

@login_required(login_url='login')
def delete_message(request, pk):

    message = Message.objects.get(id=pk)

    if request.user != message.user: #si no sos el creador del room no podes updatear

        return HttpResponse('You are not allowed here')
    
    if request.method=='POST':
        message.delete()
        return redirect('home')
        
    return render(request, 'base/delete.html', {'obj':message})



















