from django.shortcuts import render

# Create your views here.

from django.views import View
from django.contrib import messages
from datetime import timedelta
from ..models.users import Users, DEFAULT_LADDER_SCORE
from ..models.game_results import Game_Results
from ..models.game_result_users import Game_Result_Users
from ..forms.overview import GameResultFrom
from ..utils import calc_ladder_score



class Overview(View):
    def get(self, request, *args, **kwargs):
        return self.renderView(request)

    def post(self, request, *args, **kwargs):
        if (request.POST.get('add_game_result')):
            form = GameResultFrom(request.POST)

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

            if user_obj in winning_team or user_obj in losing_team:
                messages.add_message(request, messages.WARNING, 'invalid input')
                return

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
        the_form = GameResultFrom()

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

        # change to local time
        for result in game_results:
            result.created += timedelta(hours=9)

        context = {
            "users": users,
            "form": the_form,
            "game_results": game_results,
            "password": '1101',
        }

        return render(request, "ladder/overview.html", context)

    def get_race_name(self, x):
        return {
            1: "T",
            2: "P",
            3: "Z"
        }.get(x, "N")