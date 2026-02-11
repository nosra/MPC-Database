# home/forms.py
from django import forms
from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm, AuthenticationForm
from .models import CustomUser, Category, ProPlugin, Subcategory, PluginSuggestion

class CustomUserCreationForm(AdminUserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "avatar")

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "avatar")

class StaffLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_staff:
            raise forms.ValidationError("Only staff users can log in here.", code="no_staff")

PLUGIN_TYPES = [
    ("PRO", "Pro plugin"),
    ("ALT", "Alternative plugin"),
]

class StaffPluginSubmission(forms.Form):
    plugin_type = forms.ChoiceField(choices=PLUGIN_TYPES, label="Plugin type")

    # for plugin approvals. this is filled out upon selecting "use data"
    suggestion_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    plugin_name = forms.CharField(label="Plugin name", max_length=30)
    date_released = forms.DateField(
        label="Date released",
        widget=forms.DateInput(attrs={"type": "date"})
    )

    subcategory = forms.ModelMultipleChoiceField(
        queryset=Subcategory.objects.select_related("parent").order_by("parent__name", "name"),
        widget=forms.SelectMultiple()
    )

    price = forms.IntegerField(label="Price (USD)")
    description = forms.CharField(label="Description", widget=forms.Textarea(attrs={"rows": "5"}))
    size = forms.DecimalField(label="Size (MB)", max_digits=5, decimal_places=2)
    download_link = forms.URLField(label="Link to plugin page")
    image = forms.ImageField(label="Image of plugin", required=False)

    # only applies when plugin_type == ALT
    link_to_pro_plugins = forms.ModelMultipleChoiceField(
        label="Link this alternative to Pro plugins",
        queryset=ProPlugin.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Search and check the Pro plugins this alternative belongs to."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["link_to_pro_plugins"].queryset = ProPlugin.objects.order_by("name")

        # tailwind for normal fields
        base = (
            "block w-full rounded-xl border border-slate-300 bg-white px-3 py-2 "
            "text-slate-900 placeholder-slate-400 shadow-sm "
            "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        )

        for name, field in self.fields.items():
            widget = field.widget

            if isinstance(widget, (forms.FileInput, forms.ClearableFileInput)):
                continue

            # not applying input styling to checkbox list container
            if isinstance(widget, forms.CheckboxSelectMultiple):
                continue

            if isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", base + " cursor-pointer")
            elif isinstance(widget, forms.Textarea):
                widget.attrs.setdefault("class", base + " resize-y")
            else:
                widget.attrs.setdefault("class", base)

        # subcategory 
        subs = Subcategory.objects.select_related("parent").order_by("parent__name", "name")

        # creating a new dictionary that is of the following structure
        '''
        {
            "Effects": [
                (3, "Chorus"),
                (1, "Delay"),
                (2, "Reverb"),
            ],
            "Dynamics": [
                (4, "Compressor"),
                (5, "Limiter"),
            ]
        }
                
        '''
        grouped = {}
        for sub in subs:
            grouped.setdefault(sub.parent.name, []).append((sub.pk, sub.name))

        self.fields["subcategory"].choices = [
            (parent, choices) for parent, choices in grouped.items()
        ]

        # file input styling stays the same
        self.fields["image"].widget.attrs.update({
            "class": (
                "block w-full text-sm text-slate-700 "
                "file:mr-4 file:rounded-xl file:border-0 "
                "file:bg-blue-600 file:px-4 file:py-2 file:text-white file:font-semibold "
                "hover:file:bg-blue-500"
            )
        })

# suggestions for users
class SuggestionForm(forms.ModelForm):
    class Meta:
        model = PluginSuggestion
        fields = ['name', 'suggested_type', 'link', 'description']
        
        # widget section to force visible inputs
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'block w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'e.g. Serum'
            }),
            'suggested_type': forms.Select(attrs={
                'class': 'block w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'link': forms.URLInput(attrs={
                'class': 'block w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'https://example.com'
            }),
            'description': forms.Textarea(attrs={
                'class': 'block w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Tell us why this plugin is great...'
            }),
        }