from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Note
from django.shortcuts import render, redirect
import requests
from django.http import JsonResponse, HttpResponseServerError
import json


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'main/home.html'

    def get_context_data(self, *args, **kwargs):
        context = super(HomePageView, self).get_context_data(*args, **kwargs)
        query_set = Note.objects.filter(
            user=self.request.user).order_by('-last_updated')
        notes = []
        for note in query_set:
            note.content = note.content[:100] + '...'
            notes.append(note)
        context['notes'] = notes
        return context


class CreateView(LoginRequiredMixin, TemplateView):
    template_name = 'main/create.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        note = Note(title=request.POST['title'],
                    content=request.POST['editor'], user=request.user)
        note.save()
        return redirect('home')


class DetailView(LoginRequiredMixin, TemplateView):
    template_name = 'main/detail.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'note': Note.objects.get(pk=self.kwargs['id'])})

    def post(self, request, *args, **kwargs):
        note = Note.objects.get(pk=self.kwargs['id'])
        note.content = request.POST['editor']
        note.title = request.POST['title']
        print(note.content)
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
            "X-RapidAPI-Host": os.environ.get('RAPIDAPI_HOST', ''),
            "X-RapidAPI-Key": os.environ.get('RAPIDAPI_KEY', ''),
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
