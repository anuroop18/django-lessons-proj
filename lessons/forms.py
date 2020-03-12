from django import forms


class SubscribeForm(forms.Form):
    email = forms.EmailField(
        max_length=100,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )


class ContactForm(forms.Form):
    email = forms.EmailField(
        max_length=100,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    subject = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    text = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )

