from django.db import models
from django.contrib.auth.models import User

# Create your models here.
#son objetos tabla guardados en la DB que se queryean desde views 
#cada vez que se cambia algo aca hay que hacer una migracion

class Topic(models.Model):

     name = models.CharField(max_length=200)

     def __str__(self):

         return self.name

class Room(models.Model):

    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length = 200 )
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    #esto crea una relacion de muchos a muchos, muchos usuarios pueden estar en muchos rooms
    #se usa related name porque User ya esta referenciado en host y para que no cree conflicto
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta: 
       ordering = ['-updated', '-created']
   
    def __str__(self):

        return self.name
        

class Message(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE) #esto hace la relacion Hijo Padre
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta: 
        ordering = ['-updated', '-created']

    def __str__(self):

        return self.body[0:50]






