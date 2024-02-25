from django.contrib.auth.decorators import user_passes_test

def is_customer(user):
    return user.is_authenticated and user.is_customer

def is_corporate_user(user):
    return user.is_authenticated and user.is_corporate
