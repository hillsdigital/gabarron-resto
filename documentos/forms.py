from django import forms
from .models import DocumentoPDF
from .models import Empleado

from django.contrib.auth.models import User
class DocumentoPDFForm(forms.ModelForm):
    class Meta:
        model = DocumentoPDF
        fields = ['titulo', 'archivo']

class EmpleadoForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = Empleado
        fields = ['es_admin']

    def save(self, commit=True):
        empleado = super().save(commit=False)
        if not empleado.pk:
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password'],
                email=self.cleaned_data['email']
            )
            empleado.user = user
        else:
            user = empleado.user
            if self.cleaned_data['password']:
                user.set_password(self.cleaned_data['password'])
            user.email = self.cleaned_data['email']
            user.save()
        if commit:
            empleado.save()
        return empleado