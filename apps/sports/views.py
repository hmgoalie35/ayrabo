from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Sport
from django.core.urlresolvers import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from .forms import SportForm
from django.db.utils import IntegrityError
from django.shortcuts import render, redirect
from django.contrib import messages


class CreateSportView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Sport
    template_name = 'sports/create.html'
    success_url = reverse_lazy('home')
    form_class = SportForm

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.info(request, 'You do not have permission to access the requested page')
            return redirect(reverse_lazy('home'))
        return super(CreateSportView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.info(request, 'You do not have permission to access the requested page')
            return redirect(reverse_lazy('home'))
        return super(CreateSportView, self).post(request, *args, **kwargs)

    def get_success_message(self, cleaned_data):
        return '{sport} successfully created'.format(sport=self.object.name)

    def form_valid(self, form):
        try:
            return super(CreateSportView, self).form_valid(form)
        except IntegrityError:
            form.add_error('name', 'Sport with this name already exists (case-insensitive)')
            return render(self.request, self.template_name, {'form': form})
