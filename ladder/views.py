from django.shortcuts import render

# Create your views here.

from django.views import View
from django.contrib import messages
from .models import Users, Game_Results, Game_Result_Users, DEFAULT_LADDER_SCORE
from .forms import ResultFrom, SimulationForm
from .utils import calc_ladder_score, calc_rating


class HomeView(View):
    def get(self, request, *args, **kwargs):
        return self.renderView(request)

    def post(self, request, *args, **kwargs):
        if (request.POST.get('add_game_result')):
            form = ResultFrom(request.POST)

            if form.is_valid():
                self.add_game_result(request, form.cleaned_data)

        elif (request.POST.get('method') and request.POST['method'] == 'delete_game_result'):
            result = Game_Results.objects.get(pk=request.POST['pk'])
            result.valid = False
            result.save()

            members = Game_Result_Users.objects.filter(game_result_id=result.pk)
            for member in members:
                member.valid = False
                member.save()

            users = Users.objects.filter(valid=True)
            for e in users:
                e.ladder_score = DEFAULT_LADDER_SCORE
                e.save()

            game_results = Game_Results.objects.filter(valid=True).order_by('created')

            for result in game_results:
                winning_team = []
                losing_team = []
                win_users = Game_Result_Users.objects.filter(game_result_id=result.pk, is_won=True, valid=True)
                for e in win_users:
                    winning_team.append(Users.objects.get(pk=e.user_id))
                lose_users = Game_Result_Users.objects.filter(game_result_id=result.pk, is_won=False, valid=True)
                for e in lose_users:
                    losing_team.append(Users.objects.get(pk=e.user_id))

                calc_ladder_score(winning_team, losing_team)

                for e in winning_team:
                    e.save()
                for e in losing_team:
                    e.save()


        return self.renderView(request)

    def add_game_result(self, request, data):
        winning_team = []
        win_races = []
        win_is_randoms = []
        losing_team = []
        lose_races = []
        lose_is_randoms = []

        for i in range(0, 8):
            user_name = data["user_name_" + str(i)]
            race = data["race_" + str(i)]
            is_random = data["is_random_" + str(i)]

            if not user_name:
                continue

            try:
                user_obj = Users.objects.get(user_name=user_name, valid=True)
            except Users.DoesNotExist:
                continue

            if user_obj.pk == 0 or race == '0':
                continue


            if i % 2 == 0:
                winning_team.append(user_obj)
                win_races.append(race)
                win_is_randoms.append(is_random)
            else:
                losing_team.append(user_obj)
                lose_races.append(race)
                lose_is_randoms.append(is_random)

        if len(winning_team) == 0 or len(losing_team) == 0:
            messages.add_message(request, messages.WARNING, 'invalid result')
            return

        game_result_obj = Game_Results.objects.create()

        for i in range(len(winning_team)):
            Game_Result_Users.objects.create(
                game_result_id=game_result_obj.pk,
                user_id=winning_team[i].pk,
                race=win_races[i],
                is_random=win_is_randoms[i],
                is_won=True)

        for i in range(len(losing_team)):
            Game_Result_Users.objects.create(
                game_result_id=game_result_obj.pk,
                user_id=losing_team[i].pk,
                race=lose_races[i],
                is_random=lose_is_randoms[i],
                is_won=False)

        calc_ladder_score(winning_team, losing_team)

        for e in winning_team:
            e.save()
        for e in losing_team:
            e.save()


    def renderView(self, request):
        the_form = ResultFrom()

        users = Users.objects.filter(valid=True).order_by('-ladder_score')
        if len(users) > 0:
            front_score = users[0].ladder_score
            front_rank = 1
            for i in range(len(users)):
                winning_games = Game_Result_Users.objects.filter(user_id=users[i].pk, is_won=True, valid=True)
                losing_games = Game_Result_Users.objects.filter(user_id=users[i].pk, is_won=False, valid=True)
                str_stats = str(len(winning_games)) + "/" + str(len(losing_games))
                users[i].str_stats = str_stats
                if front_score == users[i].ladder_score:
                    users[i].rank = front_rank
                else:
                    front_score = users[i].ladder_score
                    users[i].rank = front_rank = i + 1


        game_results = Game_Results.objects.filter(valid=True).order_by('-created')
        for result in game_results:
            win_users = Game_Result_Users.objects.filter(game_result_id=result.pk, is_won=True, valid=True)
            str_win = ""
            for i in range(len(win_users)):
                if i != 0:
                    str_win += ", "
                str_win += Users.objects.get(pk=win_users[i].user_id).user_name
                str_win += "("
                str_win += self.get_race_name(win_users[i].race)
                str_win += ")"

            result.str_win = str_win

            lose_users = Game_Result_Users.objects.filter(game_result_id=result.pk, is_won=False, valid=True)
            str_lose = ""
            for i in range(len(lose_users)):
                if i != 0:
                    str_lose += ", "
                str_lose += Users.objects.get(pk=lose_users[i].user_id).user_name
                str_lose += "("
                str_lose += self.get_race_name(lose_users[i].race)
                str_lose += ")"

            result.str_lose = str_lose



        context = {
            "users": users,
            "form": the_form,
            "game_results": game_results,
            "password": '1101',
        }

        return render(request, "ladder/index.html", context)

    def get_race_name(self, x):
        return {
            1: "T",
            2: "P",
            3: "Z"
        }.get(x, "N")

class ManageUserView(View):
    def get(self, request, *args, **kwargs):
        return self.renderView(request)

    def post(self, request, *args, **kwargs):
        if (request.POST.get('add')):
            user_name = request.POST['user_name']
            if user_name:
                obj, created = Users.objects.get_or_create(user_name=user_name)
        elif (request.POST.get('method') and request.POST['method'] == 'delete'):
            try:
                obj = Users.objects.get(pk=request.POST['pk'])
                obj.valid = False
                obj.save()
                # return HttpResponseRedirect("/manage_user/")
            except Users.DoesNotExist:
                print("is not exist.")

        return self.renderView(request)


    def renderView(self, request):
        user_set = Users.objects.filter(valid=True)
        for user in user_set:
            wins = Game_Result_Users.objects.filter(user_id=user.pk, is_won=True, valid=True)
            loses = Game_Result_Users.objects.filter(user_id=user.pk, is_won=False, valid=True)
            str_stats = str(len(wins)) + "/" + str(len(loses))
            user.str_stats = str_stats

        context = {
            "user_set": user_set,
            "password": '1101',
        }

        return render(request, "ladder/manage_user.html", context)


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
                # self.set_simulation_form(team_a_index, form, candidate[i].user_name)
                team_a_index += 2
            else:
                # self.set_simulation_form(team_b_index, form, candidate[i].user_name)
                form.cleaned_data["user_name_" + str(team_b_index)] = candidate[i].user_name
                # form.fields["user_name_" + str(team_b_index)].value = candidate[i].user_name
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
                self.min_combination = picked
            return
        elif n < r:
            return
        else:
            picked[r - 1] = n - 1
            self.combination(n - 1, r - 1, candidate, picked)
            self.combination(n - 1, r, candidate, picked)

    def set_simulation_form(self, index, form, user_name):
        print(form["user_name_0"])
        if index == 0:
            form.user_name_0 = user_name
        elif index == 1:
            form.user_name_1 = user_name
        elif index == 2:
            form.user_name_2 = user_name
        elif index == 3:
            form.user_name_3 = user_name
        elif index == 4:
            form.user_name_4 = user_name
        elif index == 5:
            form.user_name_5 = user_name
        elif index == 6:
            form.user_name_6 = user_name
        elif index == 7:
            form.user_name_7 = user_name

    def renderView(self, request, form, team_a_rating=0, team_b_rating=0):

        context = {
            "form": form,
        }

        if (team_a_rating != 0 and team_b_rating != 0):
            context["rating_a"] = team_a_rating
            context["rating_b"] = team_b_rating

        return render(request, "ladder/simulation.html", context)