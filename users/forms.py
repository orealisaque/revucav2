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
            'cidade_ref',
            'estado_ref'
        ]
        labels = {
            'nome_artistico': 'Nome Artístico',
            'bio': 'Biografia',
            'foto_perfil': 'Foto do Perfil',
            'idade': 'Idade',
            'cidade_ref': 'Cidade',
            'estado_ref': 'Estado'
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['estado_ref'].queryset = Estado.objects.all()
        self.fields['cidade_ref'].queryset = Cidade.objects.none()
        
        if 'estado_ref' in self.data:
            try:
                estado_id = int(self.data.get('estado_ref'))
                self.fields['cidade_ref'].queryset = Cidade.objects.filter(estado_id=estado_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.estado_ref:
            self.fields['cidade_ref'].queryset = self.instance.estado_ref.cidades.all()

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['foto', 'first_name', 'last_name', 'estado_ref', 'cidade_ref', 'whatsapp', 'bio']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['estado_ref'].queryset = Estado.objects.all()
        self.fields['cidade_ref'].queryset = Cidade.objects.none()
        
        if 'estado_ref' in self.data:
            try:
                estado_id = int(self.data.get('estado_ref'))
                self.fields['cidade_ref'].queryset = Cidade.objects.filter(estado_id=estado_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.estado_ref:
            self.fields['cidade_ref'].queryset = self.instance.estado_ref.cidades.all()

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
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 
            'last_name',
            'foto',
            'whatsapp',
            'bio',
            'estado_ref',
            'cidade_ref',
            'instagram'
        ]
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'foto': 'Foto do Perfil',
            'whatsapp': 'WhatsApp',
            'bio': 'Biografia',
            'estado_ref': 'Estado',
            'cidade_ref': 'Cidade',
            'instagram': 'Instagram'
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['estado_ref'].empty_label = "Selecione um estado"
        self.fields['cidade_ref'].empty_label = "Selecione uma cidade"
        self.fields['instagram'].required = False
        
        if self.instance.estado_ref:
            self.fields['cidade_ref'].queryset = self.instance.estado_ref.cidades.all()
            
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