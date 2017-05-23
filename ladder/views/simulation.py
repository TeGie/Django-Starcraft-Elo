from django.shortcuts import render

# Create your views here.

from django.views import View
from django.contrib import messages
from ..models.users import Users
from ..forms.simulation import SimulationForm
from ..utils import calc_rating


class SimulationView(View):
    min_diff = 987654321
    min_combination = []
    def get(self, request, *args, **kwargs):
        return self.renderView(request, SimulationForm())

    def post(self, request, *args, **kwargs):
        form = SimulationForm(request.POST)

        team_a_rating = 0
        team_b_rating = 0

        if (request.POST.get('calculate_rating')):
            if form.is_valid():
                team_a_rating, team_b_rating = self.calc_rating(request, form.cleaned_data)

        elif (request.POST.get('choose_up')):
            if form.is_valid():
                self.choose_up(request, form)
                team_a_rating, team_b_rating = self.calc_rating(request, form.cleaned_data)

                form = SimulationForm(initial=form.cleaned_data)

        return self.renderView(request, form, team_a_rating, team_b_rating)

    def calc_rating(self, request, data):
        team_a_score = 0
        team_b_score = 0

        for i in range(0, 8):
            user_name = data["user_name_" + str(i)]

            if not user_name:
                continue
            try:
                user_obj = Users.objects.get(user_name=user_name, valid=True)
            except Users.DoesNotExist:
                continue

            if user_obj.pk == 0:
                continue


            if i % 2 == 0:
                team_a_score += user_obj.ladder_score
            else:
                team_b_score += user_obj.ladder_score

        if team_a_score <= 0 or team_b_score <= 0:
            messages.add_message(request, messages.WARNING, 'invalid input')
            return

        team_a_rating = calc_rating(team_a_score, team_b_score)
        team_b_rating = 1 - team_a_rating

        return team_a_rating, team_b_rating

    def choose_up(self, request, form):
        data = form.cleaned_data

        candidate = []

        for i in range(0, 8):
            user_name = data["user_name_" + str(i)]

            if not user_name:
                continue

            try:
                user_obj = Users.objects.get(user_name=user_name, valid=True)
            except Users.DoesNotExist:
                continue

            if user_obj.pk == 0:
                continue


            candidate.append(user_obj)


        team_a_number = int(len(candidate) / 2)
        picked = [-1, -1, -1, -1]
        self.min_diff = 987654321
        self.min_combination = []
        self.combination(len(candidate), team_a_number, candidate, picked)

        team_a_index = 0
        team_b_index = 1
        for i in range(len(candidate)):
            if i in self.min_combination:
                form.cleaned_data["user_name_" + str(team_a_index)] = candidate[i].user_name
                team_a_index += 2
            else:
                form.cleaned_data["user_name_" + str(team_b_index)] = candidate[i].user_name
                team_b_index += 2

        for i in range(team_a_index, 7, 2):
            form.cleaned_data["user_name_" + str(i)] = ''
        for i in range(team_b_index, 8, 2):
            form.cleaned_data["user_name_" + str(i)] = ''


    def combination(self, n, r, candidate, picked):
        if r == 0:
            team_a_score = 0
            team_b_score = 0
            for i in range(len(candidate)):
                if i in picked:
                    team_a_score += candidate[i].ladder_score
                else:
                    team_b_score += candidate[i].ladder_score


            diff = abs(team_a_score - team_b_score)

            if (diff < self.min_diff):
                self.min_diff = diff
                self.min_combination = list(picked)
            return
        elif n < r:
            return
        else:
            picked[r - 1] = n - 1
            self.combination(n - 1, r - 1, candidate, picked)
            self.combination(n - 1, r, candidate, picked)


    def renderView(self, request, form, team_a_rating=0, team_b_rating=0):

        context = {
            "form": form,
        }

        if (team_a_rating != 0 and team_b_rating != 0):
            context["rating_a"] = team_a_rating
            context["rating_b"] = team_b_rating

        return render(request, "ladder/simulation.html", context)