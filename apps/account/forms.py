from allauth.account import forms as allauth_forms
from django import forms


# @TODO set up hooks so that User.objects.create() does the necessary stuff for django all auth to work (create EmailAddress, EmailConfirmation, etc.)
class SignupForm(allauth_forms.SignupForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'autofocus': 'true'}))
    last_name = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rearrange order so first name and last name are the first fields the user needs to fill in
        # move_to_end will move to the front if False is specified
        self.fields.move_to_end('last_name', False)
        self.fields.move_to_end('first_name', False)
        # The username field has autofocus by default, remove this because first name will have autofocus
        self.fields.get('username').widget.attrs.pop('autofocus')
        # Remove all placeholder attributes
        for field_name in self.fields:
            attributes = self.fields.get(field_name).widget.attrs
            if 'placeholder' in attributes:
                attributes.pop('placeholder')
