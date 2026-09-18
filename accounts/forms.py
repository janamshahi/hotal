from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

from .models import Customer


class RegisterForm(forms.ModelForm):

    first_name = forms.CharField(
        max_length=100,
        required=True
    )

    last_name = forms.CharField(
        max_length=100,
        required=False
    )

    email = forms.EmailField(
        required=True
    )

    password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=8
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput
    )

    phone = forms.CharField(
        max_length=20,
        required=True
    )

    address = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 3
            }
        ),
        required=True
    )


    class Meta:

        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
        ]


    def clean_username(self):

        username = self.cleaned_data["username"]

        if User.objects.filter(
            username=username
        ).exists():

            raise forms.ValidationError(
                "Username already exists."
            )

        return username


    def clean_email(self):

        email = self.cleaned_data["email"]

        if User.objects.filter(
            email=email
        ).exists():

            raise forms.ValidationError(
                "Email already exists."
            )

        return email


    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get(
            "confirm_password"
        )

        if password and confirm_password:

            if password != confirm_password:

                raise forms.ValidationError(
                    "Passwords do not match."
                )

        return cleaned_data


    def save(self, commit=True):

        user = super().save(commit=False)

        user.set_password(
            self.cleaned_data["password"]
        )

        if commit:

            user.save()

            Customer.objects.create(
                user=user,
                phone=self.cleaned_data["phone"],
                address=self.cleaned_data["address"]
            )

        return user


class ProfileUpdateForm(forms.ModelForm):

    first_name = forms.CharField(
        max_length=100,
        required=True
    )

    last_name = forms.CharField(
        max_length=100,
        required=False
    )

    email = forms.EmailField(
        required=True
    )


    class Meta:

        model = Customer

        fields = [
            "phone",
            "address",
            "profile_image",
        ]


class UserUpdateForm(forms.ModelForm):

    class Meta:

        model = User

        fields = [
            "first_name",
            "last_name",
            "email",
        ]


class CustomPasswordChangeForm(PasswordChangeForm):

    pass