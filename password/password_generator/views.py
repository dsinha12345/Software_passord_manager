from django.shortcuts import render
import random
import string

# Create your views here.
def generate_password(request):
    length = int(request.GET.get('length', 12))
    include_uppercase = 'uppercase' in request.GET
    include_numbers = 'numbers' in request.GET
    include_special = 'special' in request.GET

    characters = string.ascii_lowercase
    if include_uppercase:
        characters += string.ascii_uppercase
    if include_numbers:
        characters += string.digits
    if include_special:
        characters += string.punctuation

    password = ''.join(random.choice(characters) for _ in range(length))
    
    return render(request, 'password_generator.html', {'password': password})
