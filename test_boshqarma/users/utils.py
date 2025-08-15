from .models import User
import random


def username_generator(name):

    username = ''.join(filter(str.isalnum, name.lower()))

    if not User.objects.filter(username=username).exists():
        return username
    else:
        random_username = username + str(random.randint(0, 10000))
        return username_generator(random_username)