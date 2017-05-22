from django import forms


class ResultFrom(forms.Form):

    CHOICES = (
        (0, 'Race'),
        (1, 'Terran'),
        (2, 'Protoss'),
        (3, 'Zerg'),
    )
    user_name_field = forms.CharField(
        label='',
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "user name",
                # "class": "form-control",
                # "style": "width:30%"
            }
        )
    )
    race_field = forms.ChoiceField(choices=CHOICES, label='', required=False)
    is_random_field = forms.BooleanField(
        required=False,
        label='Random',
    )

    user_name_0 = user_name_field
    race_0 = race_field
    is_random_0 = is_random_field

    user_name_1 = user_name_field
    race_1 = race_field
    is_random_1 = is_random_field

    user_name_2 = user_name_field
    race_2 = race_field
    is_random_2 = is_random_field

    user_name_3 = user_name_field
    race_3 = race_field
    is_random_3 = is_random_field

    user_name_4 = user_name_field
    race_4 = race_field
    is_random_4 = is_random_field

    user_name_5 = user_name_field
    race_5 = race_field
    is_random_5 = is_random_field

    user_name_6 = user_name_field
    race_6 = race_field
    is_random_6 = is_random_field

    user_name_7 = user_name_field
    race_7 = race_field
    is_random_7 = is_random_field


class SimulationForm(forms.Form):
    user_name_field = forms.CharField(
        label='',
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "user name",
            }
        )
    )

    user_name_0 = user_name_field
    user_name_1 = user_name_field
    user_name_2 = user_name_field
    user_name_3 = user_name_field
    user_name_4 = user_name_field
    user_name_5 = user_name_field
    user_name_6 = user_name_field
    user_name_7 = user_name_field

    def save(self):
        order = super(SimulationForm, self).save()
        return order

    def clean(self):
        cleaned_data = super(SimulationForm, self).clean()
        return cleaned_data