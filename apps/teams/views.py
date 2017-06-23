import csv
from io import TextIOWrapper

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView

from divisions.models import Division
from .forms import BulkUploadTeamsForm
from .models import Team


class BulkUploadTeamsView(LoginRequiredMixin, FormView):
    form_class = BulkUploadTeamsForm
    template_name = 'teams/team_bulk_upload.html'
    success_url = reverse_lazy('bulk_upload_teams')

    def get(self, *args, **kwargs):
        if not self.request.user.is_staff:
            return redirect(reverse_lazy('home'))
        return super(BulkUploadTeamsView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        if not self.request.user.is_staff:
            return redirect(reverse_lazy('home'))
        return super(BulkUploadTeamsView, self).post(*args, **kwargs)

    def form_valid(self, form):
        uploaded_file = form.cleaned_data.get('file')
        errors, successful_teams_created, total_csv_rows = self.parse_csv(uploaded_file)

        if len(errors) > 0:
            context = self.get_context_data()
            context['errors'] = errors
            return render(self.request, self.template_name, context)

        messages.success(self.request, '{successful_teams_created} out of {total_csv_rows} teams successfully created.'
                         .format(successful_teams_created=successful_teams_created, total_csv_rows=total_csv_rows - 1))
        return super(BulkUploadTeamsView, self).form_valid(form)

    # TODO Append unsaved team instances to list, and only save them after all teams in the file are validated.
    # TLDR; Do not save any teams to the db unless all teams in the csv are valid.
    def parse_csv(self, uploaded_file):
        # uploaded_file is a bytesio object, but DictReader needs stringio, so convert it
        csv_file = TextIOWrapper(uploaded_file.file)
        reader = csv.DictReader(csv_file)
        errors = []
        successful_teams_created = 0
        line_no = 1
        for row in reader:
            # These variables will be None if the corresponding header does not exist in the file
            team_name = row.get('Team Name', None)
            website = row.get('Website', None)
            division = row.get('Division', None)

            # Check to make sure the headings were specified in the .csv file
            if team_name is None or website is None or division is None:
                errors.append(
                        'You must include Team Name, Website and Division as headings in the .csv '
                        'on line {lineno}'.format(lineno=line_no))
                return errors, successful_teams_created, line_no

            team_name = team_name.strip()
            division = division.strip()
            website = website.strip()

            # Make sure the value of the headers aren't empty strings
            if team_name == '' or division == '':
                errors.append("Team Name and/or Division can't be blank on line {lineno}".format(lineno=line_no))
                return errors, successful_teams_created, line_no

            # Attempt to locate the division object the user wants to create a team under
            try:
                division_obj = Division.objects.get(name=division)
            except Division.DoesNotExist:
                errors.append(
                        'The division {division} does not currently exist, you need to create it '
                        'under the correct league and sport'.format(division=division))
                return errors, successful_teams_created, line_no

            # Attempt to create a team, ignoring duplicates.
            try:
                team = Team(name=team_name, website=website, division=division_obj)
                team.full_clean(exclude=['slug'])
                team.save()
                successful_teams_created += 1
            except ValidationError as e:
                errors.append('Validation failed on line {}. Error: {}'.format(line_no, ', '.join(e.messages)))
                return errors, successful_teams_created, line_no
            except IntegrityError as e:
                errors.append('Integrity Error: {}'.format(', '.join(e.messages)))
            line_no += 1

        return errors, successful_teams_created, line_no
