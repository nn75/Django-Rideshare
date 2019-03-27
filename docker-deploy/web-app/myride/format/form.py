from django import forms
from django.contrib.auth.models import User
import re


def email_check(email):
    pattern = re.compile(r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?")
    return re.match(pattern, email)

def validNumber(phone_number):
    if len(phone_number) != 12:
        return False
    for i in range(12):
        if i in [3,7]:
            if phone_number[i] != '-':
                return False
        elif not phone_number[i].isalnum():
            return False
    return True


class RegistrationForm(forms.Form):

    username = forms.CharField(label='Username', max_length=50)
    email = forms.EmailField(label='Email',)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password Confirmation', widget=forms.PasswordInput)

    name = forms.CharField(label='Name', max_length=50)
    phone = forms.CharField(label='Phone', max_length=50, required=True)

    # Use clean methods to define custom validation rules

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if len(username) < 6:
            raise forms.ValidationError("Your username must be at least 6 characters long.")
        elif len(username) > 50:
            raise forms.ValidationError("Your username is too long.")
        else:
            filter_result = User.objects.filter(username__exact=username)
            if len(filter_result) > 0:
                raise forms.ValidationError("Your username already exists.")

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email_check(email):
            filter_result = User.objects.filter(email__exact=email)
            if len(filter_result) > 0:
                raise forms.ValidationError("Your email already exists.")
        else:
            raise forms.ValidationError("Please enter a valid email.")

        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        if len(password1) < 6:
            raise forms.ValidationError("Your password is too short.")
        elif len(password1) > 20:
            raise forms.ValidationError("Your password is too long.")

        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password mismatch. Please enter again.")

        return password2

    def clean_name(self):
        name = self.cleaned_data.get('name')

        if len(name) < 6:
            raise forms.ValidationError("Your name is too short.")
        elif len(name) > 48:
            raise forms.ValidationError("Your name is too long.")
        return name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if not validNumber(phone):
            raise forms.ValidationError("'Please enter a phone number in the format XXX-XXX-XXXX: '")

        return phone

class LoginForm(forms.Form):

    username = forms.CharField(label='Username', max_length=50, initial='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput(render_value = True), initial='Password')
    username.widget.attrs.update({'class': "dan"})
    password.widget.attrs.update({'class': "dan"})
    # Use clean methods to define custom validation rules

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if email_check(username):
            filter_result = User.objects.filter(email__exact=username)
            if not filter_result:
                raise forms.ValidationError("This email does not exist.")
        else:
            filter_result = User.objects.filter(username__exact=username)
            if not filter_result:
                raise forms.ValidationError("This username does not exist. Please register first.")

        return username

class CustomerForm(forms.Form):

    name = forms.CharField(label='name', max_length=50, required=True)
    phone = forms.CharField(label='phone', max_length=50, required=True)

class DriverForm(forms.Form):

    license = forms.CharField(label='license', max_length=10, required=True)
    vehicle_level = forms.CharField(label='vehicle_level', max_length=1, required=True)
    special_service = forms.CharField(label='special_service', max_length=200, required=False)



class PwdChangeForm(forms.Form):

    old_password = forms.CharField(label='Old password', widget=forms.PasswordInput)

    password1 = forms.CharField(label='New Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password Confirmation', widget=forms.PasswordInput)

    # Use clean methods to define custom validation rules

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        if len(password1) < 6:
            raise forms.ValidationError("Your password is too short.")
        elif len(password1) > 20:
            raise forms.ValidationError("Your password is too long.")

        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password mismatch. Please enter again.")

        return password2
