from social_core.pipeline.partial import partial
from django.shortcuts import redirect
from django.urls import reverse
from social_django.models import UserSocialAuth
from django.core.exceptions import ObjectDoesNotExist
from social_core.pipeline.user import create_user
# from social_core.exceptions import AuthAlreadyAssociated

@partial
def collect_username(strategy, backend, details, user=None, is_new=False, *args, **kwargs):
    """
    Custom pipeline step to collect the username for new users.
    """
    if user or not is_new:
        return  # Skip if the user already exists or is not new

    # Get the social auth UID
    social_uid = kwargs.get('uid')
    if not social_uid:
        return  # Skip if no UID is found

    # Store the social auth UID in the session for later use
    strategy.session_set('social_auth_uid', social_uid)

    # Redirect to the collect-username endpoint
    return redirect(reverse('collect_username'))


from social_core.exceptions import AuthAlreadyAssociated

from django.core.exceptions import ObjectDoesNotExist






def save_user_data(strategy, details, backend, user=None, *args, **kwargs):
    """
    Pipeline function to check if a user exists by email.
    If the user exists, log them in. If not, create a new user.
    """
    # Debug: Print the details dictionary to verify its structure
    print("Details from provider:", details)

    # Access email from the details dictionary
    email = details.get('email')
    if not email:
        print("No email provided in details.")  # Debug: Log missing email
        return  # Skip if no email is provided

    User = strategy.storage.user.user_model()  # Get the User model

    try:
        # Check if the user already exists in the database
        user = User.objects.get(email=email)
        print("User found in database:", user)  # Debug: Print existing user
    except User.DoesNotExist:
        # If the user does not exist, create a new user
        print("Creating new user...")  # Debug: Log new user creation

        # Generate a username if not provided
        username = details.get('username')
        if not username:
            # Use the email (without the domain) as the username
            username = email.split('@')[0]

        # Manually create the user
        user = User.objects.create_user(
            username=username,  # Pass the username
            email=email,
            first_name=details.get('first_name', ''),
            last_name=details.get('last_name', ''),
            # Add any other required fields here
        )
        print("New user created:", user)  # Debug: Print new user

    return {'user': user}