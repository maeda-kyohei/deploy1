from django import forms
from .models import Users, Comment
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import DateInput
from django.core.exceptions import ValidationError

class RegistForm(forms.ModelForm):
    username = forms.CharField(label='名前')
    age = forms.IntegerField(label='年齢', min_value=0)
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())

    class Meta:
        model = Users
        fields = ['username', 'age', 'email', 'password']
    
    def save(self, commit=False):
        user = super().save(commit=False)
        validate_password(self.cleaned_data['password'], user)
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user


# class UserLoginForm(forms.Form):
#     email = forms.EmailField(label='メールアドレス')
#     password = forms.CharField(label='パスワード', widget=forms.PasswordInput())
class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    # username = forms.EmailField(label='メールアドレス')
    username = forms.CharField(label='名前')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())
    remember = forms.BooleanField(label='ログイン状態を保持する', required=False)


class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        
        for field in self.fields.values():  # bootstrapで使用するform-controlクラス
            field.widget.attrs['class'] = 'form-control'
            
    class Meta:
        model = Users
        fields = ('username', 'email', 'age')
        help_texts = {
            'username': None,
            'email':None,
        }
        
class AnalysisPeriodForm(forms.Form):
    start_day = forms.DateField(label="開始日", widget=DateInput())
    end_day = forms.DateField(label="終了日", widget=DateInput())

    def clean(self):
        period = super().clean()
        start_day = period["start_day"]
        end_day = period["end_day"]
        if start_day > end_day:
            raise ValidationError("開始日と終了日が前後しています。")
        return period

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
