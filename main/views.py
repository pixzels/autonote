from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Note
from django.shortcuts import render, redirect
import requests
from django.http import JsonResponse
import json
from django.conf import settings


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'main/home.html'

    def get(self, request, *args, **kwargs):
        query_set = Note.objects.filter(
            user=self.request.user).order_by('-last_updated')
        notes = []
        for note in query_set:
            note.content = note.content[:100] + '...' if note.content else ''
            notes.append(note)

        return render(request, self.template_name, {'notes': notes})


class CreateView(LoginRequiredMixin, TemplateView):
    template_name = 'main/create.html'

    def post(self, request, *args, **kwargs):
        title, editor = request.POST.get(
            'title', ''), request.POST.get('editor', '')

        note = Note(title=title,
                    content=editor, user=request.user)
        if title:
            note.save()
        return redirect('home')


class DetailView(LoginRequiredMixin, TemplateView):
    template_name = 'main/detail.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'note': Note.objects.get(pk=self.kwargs['id'])})

    def post(self, request, *args, **kwargs):
        note = Note.objects.get(pk=self.kwargs['id'])
        note.content = request.POST.get('editor', '')
        note.title = request.POST.get('title', '')
        if note.title:
            note.save()
        return redirect('home')


class DeleteView(LoginRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        note = Note.objects.get(pk=self.kwargs['id'])
        note.delete()
        return redirect('home')


class SummarizeView(LoginRequiredMixin, TemplateView):

    def post(self, request, *args, **kwargs):
        headers = {
            "X-RapidAPI-Host": settings.RAPIDAPI_HOST,
            "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
            "Content-Type": "application/json"
        }
        data = {
            "url": request.POST.get('url', ''),
            "sentnum": int(request.POST['n']),
            "text": request.POST['editor'] if request.POST.get('url', '') == '' else ''
        }
        r = requests.post(
            'https://textanalysis-text-summarization.p.rapidapi.com/text-summarizer', json=data, headers=headers)

        if r.status_code == 200:
            data = r.json()['sentences']
            sentences = []
            for i, s in enumerate(data):
                sentences.append(f'{i+1}. {s}\n')
            return JsonResponse("".join(sentences), safe=False)
        else:
            return HttpResponseServerError("Something went wrong")
