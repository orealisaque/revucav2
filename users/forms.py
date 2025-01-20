from django import forms
from allauth.account.forms import SignupForm
from .models import CustomUser, AcompanhanteProfile, Estado, Cidade
from django.urls import reverse_lazy
from datetime import date
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(
        max_length=30, 
        label='Nome',
        widget=forms.TextInput(attrs={'placeholder': 'Seu nome'})
    )
    whatsapp = forms.CharField(
        max_length=15, 
        label='WhatsApp',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '(99) 99999-9999'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('first_name', css_class='form-input'),
            Field('email', css_class='form-input'),
            Field('whatsapp', css_class='form-input'),
            Field('password1', css_class='form-input'),
            Field('password2', css_class='form-input'),
        )
        
        # Remove labels e adiciona placeholders
        self.fields['email'].widget.attrs['placeholder'] = 'Seu e-mail'
        self.fields['password1'].widget.attrs['placeholder'] = 'Senha'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirme sua senha'
        
    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.whatsapp = self.cleaned_data.get('whatsapp', '')
        user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = AcompanhanteProfile
        fields = [
            'nome_artistico',
            'bio',
            'foto_perfil',
            'idade',
            'estado',
            'cidade'
        ]
        labels = {
            'nome_artistico': 'Nome Artístico',
            'bio': 'Biografia',
            'foto_perfil': 'Foto do Perfil',
            'idade': 'Idade',
            'estado': 'Estado',
            'cidade': 'Cidade'
        }
        widgets = {
            'nome_artistico': forms.TextInput(attrs={'class': 'form-input bg-dark-700 text-white border-dark-600'}),
            'bio': forms.Textarea(attrs={'class': 'form-textarea bg-dark-700 text-white border-dark-600', 'rows': 4}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-input bg-dark-700 text-white border-dark-600'}),
            'idade': forms.NumberInput(attrs={'class': 'form-input bg-dark-700 text-white border-dark-600'}),
            'estado': forms.Select(attrs={'class': 'form-select bg-dark-700 text-white border-dark-600'}),
            'cidade': forms.Select(attrs={'class': 'form-select bg-dark-700 text-white border-dark-600'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['estado'].queryset = Estado.objects.all()
        self.fields['cidade'].queryset = Cidade.objects.none()
        
        if 'estado' in self.data:
            try:
                estado_id = int(self.data.get('estado'))
                self.fields['cidade'].queryset = Cidade.objects.filter(estado_id=estado_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.estado:
            self.fields['cidade'].queryset = Cidade.objects.filter(estado=self.instance.estado)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['foto', 'first_name', 'last_name', 'estado', 'cidade', 'whatsapp', 'bio']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['estado'].queryset = Estado.objects.all()
        self.fields['cidade'].queryset = Cidade.objects.none()
        
        if 'estado' in self.data:
            try:
                estado_id = int(self.data.get('estado'))
                self.fields['cidade'].queryset = Cidade.objects.filter(estado_id=estado_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.estado:
            self.fields['cidade'].queryset = Cidade.objects.filter(estado=self.instance.estado)

    def clean_whatsapp(self):
        whatsapp = self.cleaned_data.get('whatsapp')
        if whatsapp:
            # Remove todos os caracteres não numéricos
            numbers_only = ''.join(filter(str.isdigit, whatsapp))
            if len(numbers_only) != 11:
                raise forms.ValidationError('O número deve ter 11 dígitos (DDD + número)')
            # Formata o número
            return f'({numbers_only[:2]}) {numbers_only[2:7]}-{numbers_only[7:]}'
        return whatsapp

class ProfileEditForm(forms.ModelForm):
    estado = forms.ModelChoiceField(
        queryset=Estado.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select bg-dark-700 text-white border-dark-600'})
    )
    
    cidade = forms.ModelChoiceField(
        queryset=Cidade.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select bg-dark-700 text-white border-dark-600'})
    )
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'whatsapp', 'estado', 'cidade', 'bio', 'foto']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input bg-dark-700 text-white border-dark-600'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input bg-dark-700 text-white border-dark-600'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-input bg-dark-700 text-white border-dark-600'}),
            'bio': forms.Textarea(attrs={'class': 'form-textarea bg-dark-700 text-white border-dark-600', 'rows': 4}),
            'foto': forms.FileInput(attrs={'class': 'form-input bg-dark-700 text-white border-dark-600'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.estado:
            self.fields['cidade'].queryset = Cidade.objects.filter(estado=self.instance.estado)

    def clean_whatsapp(self):
        whatsapp = self.cleaned_data.get('whatsapp')
        if whatsapp:
            # Remove todos os caracteres não numéricos
            numbers_only = ''.join(filter(str.isdigit, whatsapp))
            if len(numbers_only) != 11:
                raise forms.ValidationError('O número deve ter 11 dígitos')
            return numbers_only
        return whatsapp
        
    def clean_instagram(self):
        instagram = self.cleaned_data.get('instagram')
        if instagram:
            # Remove @ se existir
            return instagram.lstrip('@')
        return instagram 