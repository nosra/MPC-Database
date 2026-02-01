from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.db.models import Q
from django.urls import reverse
from .models import ProPlugin, AlternativePlugin, CATEGORIES
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import user_passes_test
from .forms import StaffPluginSubmission
from django.contrib import messages

def home(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render())

# ---------
# plugins routers
# ---------

def plugins(request):
    tab = request.GET.get("tab", "pro")
    category = request.GET.get("category")
    search_query = (request.GET.get("q") or "").strip()

    # figure out which list we're showing
    if tab == "alt":
        plugins_qs = AlternativePlugin.objects.all()
        active_tab = "alt"
    else:
        plugins_qs = ProPlugin.objects.all()
        active_tab = "pro"

    # validate & apply category filter
    valid_codes = dict(CATEGORIES).keys()  # {'EFX', 'SYN', ...}
    if category in valid_codes:
        plugins_qs = plugins_qs.filter(category=category)
        active_category = category
    else:
        active_category = None # "All"

    # apply search filter if there's a query
    if search_query:
        plugins_qs = plugins_qs.filter(
            Q(name__icontains=search_query)
            # other filters can be requested too
            # | Q(description__icontains=search_query)
            # | Q(company__icontains=search_query)
        )

    context = {
        "plugins": plugins_qs,
        "active_tab": active_tab,
        "active_category": active_category,
        "search_query": search_query,
    }

    # ajax request, only return the list HTML
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "partials/plugin_cards.html", context)

    # otherwise full page render
    return render(request, "plugins.html", context)


def plugin_detail(request, pk):
    plugin = get_object_or_404(ProPlugin, pk=pk)
    return render(request, "plugin_detail.html", {"plugin": plugin})


def alt_plugin_detail(request, pk):
    plugin = get_object_or_404(AlternativePlugin, pk=pk)
    return render(request, 'alt_plugin_detail.html', {"plugin": plugin})

# ---------
# submissions routers
# ---------
def staff_check(user):
    return user.is_staff

# handled by logout view (built in class)
def staff_logout(user):
    pass

@user_passes_test(staff_check, login_url="staff_login")
def staff_dashboard(request):
    # post requests here will refer to adding a new plugin
    if request.method == "POST":
        # create a form instance, populate it with the data from the request
        form = StaffPluginSubmission(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data

            common = dict(
                submitter=request.user,
                name=data["plugin_name"],
                date_released=data["date_released"],
                category=data["category"],
                price=data["price"],
                description=data["description"],
                size=data["size"],
                download_link=data["download_link"],
                image=data.get("image"),
            )

            if data["plugin_type"] == "PRO":
                ProPlugin.objects.create(**common)
            else:
                alt = AlternativePlugin.objects.create(**common)
                for pro in data["link_to_pro_plugins"]:
                    pro.alternatives.add(alt)

            messages.success(request, "Plugin submitted!")
            return redirect("staff_dashboard")
        
    else:
        form = StaffPluginSubmission()
    return render(request, "staff_dashboard.html", {"form": form})

def about(request):
    return render(request, "about.html")

def search_plugins(request):
    query = request.GET.get('q', '')
    results = []

    if len(query) > 1:
        # search free Alternatives
        alts = AlternativePlugin.objects.filter(name__icontains=query)[:3] # only going up to 3 plugins
        for item in alts:
            results.append({
                'name': item.name,
                'category': item.get_category_display(),
                'type': 'Free',
                'image': item.image_url,
                'url': reverse('alt_plugin_detail', args=[item.pk]) 
            })

        # search Pro Plugins
        pros = ProPlugin.objects.filter(name__icontains=query)[:3]
        for item in pros:
            results.append({
                'name': item.name,
                'category': item.get_category_display(),
                'type': 'Pro/Paid',
                'image': item.image_url,
                'url': reverse('plugin_detail', args=[item.pk]) 
            })

    return JsonResponse({'results': results})