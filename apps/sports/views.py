from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.shortcuts import redirect, render
from django.views import generic
from django.views.generic.base import ContextMixin

from .forms import CreateSportRegistrationForm
from .models import SportRegistration, Sport


class FinishSportRegistrationView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'sports/sport_registration_finish.html'


class SportRegistrationInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super(SportRegistrationInlineFormSet, self).clean()
        sports_already_seen = []
        for form in self.forms:
            sport = form.cleaned_data.get('sport')
            if sport is not None:
                if sport in sports_already_seen:
                    form.add_error('sport',
                                   'Only one form can have {sport} selected. Choose another sport, or the "---------" value.'.format(
                                           sport=sport.name))
                else:
                    sports_already_seen.append(sport)


class CreateSportRegistrationView(LoginRequiredMixin, ContextMixin, generic.View):
    template_name = 'sports/sport_registration_create.html'
    already_registered_msg = 'You have already registered for all available sports. ' \
                             'Check back later to see if any new sports have been added.'

    def get_context_data(self, **kwargs):
        context = super(CreateSportRegistrationView, self).get_context_data(**kwargs)
        sports_already_registered_for = SportRegistration.objects.filter(user=self.request.user).values_list('sport_id')
        context['sport_count'] = Sport.objects.count() - len(sports_already_registered_for)
        context['user_registered_for_all_sports'] = context.get('sport_count') == 0
        sport_registration_form_set = inlineformset_factory(User, SportRegistration, form=CreateSportRegistrationForm,
                                                            formset=SportRegistrationInlineFormSet,
                                                            extra=0,
                                                            min_num=1, max_num=context.get('sport_count'),
                                                            validate_min=True, validate_max=True, can_delete=False)
        context['formset'] = sport_registration_form_set(self.request.POST or None,
                                                         form_kwargs={
                                                             'sports_already_registered_for': sports_already_registered_for})
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if context.get('user_registered_for_all_sports'):
            messages.info(request, self.already_registered_msg)
            return redirect(reverse('home'))
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if context.get('user_registered_for_all_sports'):
            messages.info(request, self.already_registered_msg)
            return redirect(reverse('home'))

        formset = context.get('formset')
        if formset.is_valid():
            for form in formset.forms:
                form.instance.user = request.user
                form.instance.set_roles(form.cleaned_data.get('roles', []))
                form.save()
            return redirect(reverse('sport:finish_sport_registration'))

        return render(request, self.template_name, context)
