from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Gestionnaire, Administrateur, Employe, User
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Group

# rédéfinition de la création d'utilisateurs dans la panel admin:
# https://docs.djangoproject.com/en/2.0/topics/auth/customizing/#a-full-example

class EmployeInline(admin.StackedInline):
  model = Employe
  can_delete = False
  verbose_name = "employé"

class GestionnaireInline(admin.StackedInline):
  model = Gestionnaire
  can_delete = False
  verbose_name = "gestionnaire"

class UserCreationForm(forms.ModelForm):
  """A form for creating new users. Includes all the required
  fields, plus a repeated password."""
  password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
  password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

  class Meta:
    model = User
    fields = '__all__'

  def clean_password2(self):
    # Check that the two password entries match
    password1 = self.cleaned_data.get("password1")
    password2 = self.cleaned_data.get("password2")
    if password1 and password2 and password1 != password2:
      raise forms.ValidationError("Passwords don't match")
    return password2

  def save(self, commit=True):
    # Save the provided password in hashed format
    user = super().save(commit=False)
    user.set_password(self.cleaned_data["password1"])
    if commit:
      user.save()
    return user


class UserChangeForm(forms.ModelForm):
  """A form for updating users. Includes all the fields on
  the user, but replaces the password field with admin's
  password hash display field.ckclear
  """
  password = ReadOnlyPasswordHashField()

  class Meta:
    model = User
    fields = '__all__'

  def clean_password(self):
    # Regardless of what the user provides, return the initial value.
    # This is done here, rather than on the field, because the
    # field does not have access to the initial value
    return self.initial["password"]


class UserAdmin(BaseUserAdmin):
  inlines = (EmployeInline, GestionnaireInline, )
  # The forms to add and change user instances
  form = UserChangeForm
  add_form = UserCreationForm
  add_fieldsets = (
    (None, {
      'classes': ('wide',),
      'fields': ('username', 'user_type', 'password1', 'password2')}
    ),
  )


# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
