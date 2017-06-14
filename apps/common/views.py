from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, Http404, redirect
from django.urls import reverse
from django.views import generic
from django.views.generic.base import ContextMixin

from escoresheet.utils import handle_sport_not_configured
from escoresheet.utils.exceptions import SportNotConfiguredException
from escoresheet.utils.mixins import AccountAndSportRegistrationCompleteMixin
from leagues.models import League
from players.models import AbstractPlayer
from sports.models import SportRegistration
from teams.models import Team

MIN_FORMS = 1
MAX_FORMS = 10


class BaseCreateRelatedObjectsView(LoginRequiredMixin, ContextMixin, AccountAndSportRegistrationCompleteMixin,
                                   generic.View):
    already_registered_msg = 'You have already registered for all available {}.'

    def get_template_name(self):
        raise NotImplementedError()

    def get_form_class(self, sport_name):
        raise NotImplementedError()

    def get_formset_prefix(self):
        raise NotImplementedError()

    def get_model_class(self, sport_name):
        raise NotImplementedError()

    def get_formset_class(self, sport_name):
        raise NotImplementedError()

    def get_formset_helper_class(self, sport_name):
        raise NotImplementedError()

    def get_role(self):
        raise NotImplementedError()

    def get_context_data(self, **kwargs):
        context = super(BaseCreateRelatedObjectsView, self).get_context_data(**kwargs)

        sr = get_object_or_404(SportRegistration.objects.select_related('sport'), pk=kwargs.get('pk'))
        if sr.user_id != self.request.user.id:
            raise Http404

        sport_name = sr.sport.name
        form_cls = self.get_form_class(sport_name)
        model_cls = self.get_model_class(sport_name)
        formset_cls = self.get_formset_class(sport_name)
        formset_helper_cls = self.get_formset_helper_class(sport_name)
        if form_cls is None or model_cls is None or formset_helper_cls is None:
            raise SportNotConfiguredException(sport_name)

        role = self.get_role()

        FormSet = forms.modelformset_factory(model_cls, form=form_cls, formset=formset_cls, extra=0,
                                             min_num=MIN_FORMS, max_num=MAX_FORMS, validate_min=True, validate_max=True,
                                             can_delete=False)
        filter_kwargs = {'user': self.request.user}
        if role == 'Referee':
            field = 'league'
            count = League.objects.filter(sport=sr.sport).count()
            filter_kwargs['league__sport'] = sr.sport
        else:
            field = 'team'
            count = Team.objects.filter(division__league__sport=sr.sport).count()
            if role == 'Player':
                filter_kwargs['sport'] = sr.sport
            else:
                filter_kwargs['team__division__league__sport'] = sr.sport
        # We want to include inactive objects in this query.
        already_registered_for = model_cls.objects.filter(**filter_kwargs).only(field).values_list(field, flat=True)
        context['user_registered_for_all'] = already_registered_for.count() == count
        context['formset'] = FormSet(self.request.POST or None,
                                     queryset=model_cls.objects.none(),
                                     prefix=self.get_formset_prefix(),
                                     form_kwargs={'sport': sr.sport,
                                                  'user': self.request.user,
                                                  'already_registered_for': already_registered_for
                                                  }
                                     )
        context['helper'] = formset_helper_cls
        context['sport_name'] = sport_name
        context['sport_registration'] = sr
        context['role'] = role
        return context

    def get(self, *args, **kwargs):
        try:
            context = self.get_context_data(**kwargs)
        except SportNotConfiguredException as e:
            return handle_sport_not_configured(self.request, self, e)
        if context.get('user_registered_for_all', False):
            role = self.get_role()
            sr = context.get('sport_registration')
            messages.info(self.request, self.already_registered_msg.format('leagues' if role == 'Referee' else 'teams'))
            return redirect(sr.get_absolute_url())

        return render(self.request, self.get_template_name(), context)

    def post(self, *args, **kwargs):
        try:
            context = self.get_context_data(**kwargs)
        except SportNotConfiguredException as e:
            return handle_sport_not_configured(self.request, self, e)

        if context.get('user_registered_for_all', False):
            role = self.get_role()
            sr = context.get('sport_registration')
            messages.info(self.request, self.already_registered_msg.format('leagues' if role == 'Referee' else 'teams'))
            return redirect(sr.get_absolute_url())

        formset = context.get('formset')
        sport_registration = context.get('sport_registration')
        role = context.get('role')
        if role is not None and role not in sport_registration.roles:
            sport_registration.set_roles([role], append=True)
            self.request.session['was_role_added'] = True
        for form in formset:
            if isinstance(form.instance, AbstractPlayer):
                form.instance.sport = sport_registration.sport
        if formset.is_valid():
            instances = formset.save()
            if role == 'Referee':
                names = [obj.league.abbreviated_name for obj in instances]
            else:
                names = [obj.team.name for obj in instances]
            messages.success(self.request,
                             'You have been registered as a {} for the {}.'.format(role.lower(), ', '.join(names)))
            self.request.session.pop('was_role_added', None)
            next_role = sport_registration.get_next_namespace_for_registration()
            if next_role is None:
                # No remaining roles need to be filled out for this sport registration, mark as complete.
                sport_registration.is_complete = True
                sport_registration.save()
                # See if there are remaining incomplete sport registrations.
                next_sr = self.request.session.pop('next_sport_registration', None)
                if next_sr is not None:
                    next_sr_id = next_sr.get('id')
                    next_sr_role = next_sr.get('role')
                    url = 'sportregistrations:{role}:create'.format(role=next_sr_role)
                    return redirect(reverse(url, kwargs={'pk': next_sr_id}))
                # All incomplete sport registrations have been completed.
                return redirect('home') if self.request.session.get('is_user_currently_registering', False) \
                    else redirect(sport_registration.get_absolute_url())
            else:
                url = 'sportregistrations:{role}:create'.format(role=next_role)
                return redirect(reverse(url, kwargs={'pk': sport_registration.id}))
        if self.request.session.pop('was_role_added', False):
            sport_registration.remove_role(role)
        return render(self.request, self.get_template_name(), context)
