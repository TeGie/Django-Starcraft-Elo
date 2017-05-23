from django import forms



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