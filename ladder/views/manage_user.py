from django.shortcuts import render

# Create your views here.

from django.views import View
from ..models.users import Users
from ..models.game_result_users import Game_Result_Users



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

