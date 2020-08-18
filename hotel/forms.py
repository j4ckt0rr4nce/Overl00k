from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from .models import Profile, Contact, Post, Message
from .fields import CommaSeparatedUserField


class LoginForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

        widgets = {
            'username' : forms.TextInput(attrs={}),
            'password' : forms.TextInput(attrs={}),
        }



class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

        widgets = {
            'username' : forms.TextInput(attrs={}),
            'email' : forms.TextInput(attrs={}),
            'password1' : forms.TextInput(attrs={}),
            'password2' : forms.TextInput(attrs={}),
        }



class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

        widgets = {
            'username' : forms.TextInput(attrs={}),
            'email' : forms.TextInput(attrs={}),
        }


            
class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['image', 'address', 'city', 'country', 'phone']

        widgets = {
            'address' : forms.TextInput(attrs={}),
            'city' : forms.TextInput(attrs={}),
            'country' : forms.TextInput(attrs={}),
            'phone' : forms.TextInput(attrs={}),
        }



class ContactForm(forms.ModelForm):

    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        
        widgets = {
            'name' : forms.TextInput(attrs={'class': 'input', 'placeholder' : 'Enter your full name'}),
            'email' : forms.TextInput(attrs={'class': 'input', 'placeholder' : 'Enter your email address'}),
            'subject' : forms.TextInput(attrs={'class': 'input', 'placeholder' : 'Enter your subject'}),
            'message': forms.Textarea(attrs={'class': 'textarea', 'rows': 10, 'placeholder' : 'Your message here...'}),
        }



class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['title', 'content']
        
        widgets = {
            'title' : forms.TextInput(attrs={'class': 'input', 'placeholder' : 'Enter your title'}),
            'content' : forms.TextInput(attrs={'class': 'input', 'placeholder' : 'Enter your content'}),
            
        }



class ComposeForm(forms.Form):
    recipient = CommaSeparatedUserField(label=u"Recipient")
    subject = forms.CharField(label=u"Subject", max_length=140)
    body = forms.CharField(label=u"Body",
        widget=forms.Textarea(attrs={'rows': '12', 'cols':'55'}))


    def __init__(self, *args, **kwargs):
        recipient_filter = kwargs.pop('recipient_filter', None)
        super(ComposeForm, self).__init__(*args, **kwargs)
        if recipient_filter is not None:
            self.fields['recipient']._recipient_filter = recipient_filter


    def save(self, sender, parent_msg=None):
        recipients = self.cleaned_data['recipient']
        subject = self.cleaned_data['subject']
        body = self.cleaned_data['body']
        message_list = []
        for r in recipients:
            msg = Message(
                sender = sender,
                recipient = r,
                subject = subject,
                body = body,
            )
            if parent_msg is not None:
                msg.parent_msg = parent_msg
                parent_msg.replied_at = timezone.now()
                parent_msg.save()
            msg.save()
            message_list.append(msg)
            """
            if notification:
                if parent_msg is not None:
                    notification.send([sender], "messages_replied", {'message': msg,})
                    notification.send([r], "messages_reply_received", {'message': msg,})
                else:
                    notification.send([sender], "messages_sent", {'message': msg,})
                    notification.send([r], "messages_received", {'message': msg,})
             """       
        return message_list