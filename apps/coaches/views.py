from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic

from ayrabo.utils.mixins import HasPermissionMixin
from coaches.models import Coach
from sports.models import Sport
from .forms import CoachUpdateForm


class CoachesUpdateView(LoginRequiredMixin,
                        HasPermissionMixin,
                        SuccessMessageMixin,
                        generic.UpdateView):
    """
    Even though sport is not used here at all, we want to still require a valid sport slug in the url.
    """
    template_name = 'coaches/coaches_update.html'
    pk_url_kwarg = 'coach_pk'
    context_object_name = 'coach'
    success_message = 'Your coach information has been updated.'
    success_url = reverse_lazy('home')
    queryset = Coach.objects.select_related('team')
    form_class = CoachUpdateForm

    def _get_sport(self):
        if hasattr(self, 'sport'):
            return self.sport
        self.sport = get_object_or_404(Sport, slug=self.kwargs.get('slug'))
        return self.sport

    def has_permission_func(self):
        user = self.request.user
        coach = self.get_object()
        return user.id == coach.user_id

    def form_valid(self, form):
        if form.has_changed():
            return super().form_valid(form)
        return redirect(self.get_success_url())

    def get(self, request, *args, **kwargs):
        self._get_sport()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._get_sport()
        return super().post(request, *args, **kwargs)
