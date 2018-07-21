from itertools import groupby

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import generic

from ayrabo.utils.mappings import SPORT_PLAYER_MODEL_MAPPINGS
from ayrabo.utils.mixins import PreSelectedTabMixin
from coaches.models import Coach
from managers.models import Manager
from referees.models import Referee
from scorekeepers.models import Scorekeeper
from sports.models import SportRegistration
from userprofiles.models import UserProfile
from .forms import UserProfileCreateForm, UserProfileUpdateForm


class UserProfileCreateView(LoginRequiredMixin, generic.CreateView):
    model = UserProfile
    template_name = 'userprofiles/userprofile_create.html'
    success_url = reverse_lazy('sports:register')
    form_class = UserProfileCreateForm

    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, 'userprofile'):
            return redirect(reverse('home'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class UserProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, PreSelectedTabMixin, generic.UpdateView):
    model = UserProfile
    form_class = UserProfileUpdateForm
    template_name = 'userprofiles/userprofile_update.html'
    success_url = reverse_lazy('account_home')
    success_message = 'Your account has been updated.'
    context_object_name = 'userprofile'
    valid_tabs = ['my_account', 'my_sports']
    default_tab = 'my_account'

    def get_related_objects(self, sport):
        user = self.request.user
        player_model_cls = SPORT_PLAYER_MODEL_MAPPINGS.get(sport.name)
        coaches = Coach.objects.filter(user=user, team__division__league__sport=sport).select_related(
            'team__division__league__sport')
        managers = Manager.objects.filter(user=user, team__division__league__sport=sport).select_related(
            'team__division__league__sport')
        referees = Referee.objects.filter(user=user, league__sport=sport).select_related('league__sport')
        players = player_model_cls.objects.filter(user=user, sport=sport).select_related(
            'team__division', 'sport') if player_model_cls else []
        scorekeepers = Scorekeeper.objects.filter(user=user, sport=sport).select_related('sport')
        return {
            'coach': coaches,
            'manager': managers,
            'player': players,
            'referee': referees,
            'scorekeeper': scorekeepers,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sport_registrations = SportRegistration.objects.filter(user=self.request.user).exclude(role=None).order_by(
            'sport').select_related('sport', 'user')
        data = {}
        for sport, registrations in groupby(sport_registrations, key=lambda obj: obj.sport):
            roles = sorted([sr.get_role_display() for sr in registrations])
            data[sport] = {
                'roles': roles,
                'related_objects': self.get_related_objects(sport)
            }
        context['data'] = data
        return context

    def get_object(self, queryset=None):
        return self.request.user.userprofile

    def form_valid(self, form):
        if form.has_changed():
            return super().form_valid(form)
        else:
            return redirect(reverse('account_home'))
