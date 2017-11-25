from django import forms


class LoginForm(forms.Form):
    """
    Capture the login details
    """
    environment = forms.ChoiceField(choices=(('Production','Production'),('Sandbox','Sandbox')))

