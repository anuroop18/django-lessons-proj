import logging
from django.http import (Http404, HttpResponseBadRequest)
from django.shortcuts import render
from django.views.generic import TemplateView

from lessons.models import Subscribtion
from lessons.forms import SubscribeForm


logger = logging.getLogger(__name__)


def handler500(request):
    return render(request, "lessons/500.html")


class PageView(TemplateView):
    pass


def subscribe(request):

    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            subscribe = Subscribtion(email=form.cleaned_data['email'])
            subscribe.save()
            return render(request, 'lessons/thankyou.html')
    else:
        form = SubscribeForm()

    return render(
        request,
        'lessons/subscribe.html',
        {'form': form}
    )
