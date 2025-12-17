from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.db.models import Q              # 🔸 add this
from .models import ProPlugin, AlternativePlugin, CATEGORIES
from django.contrib.auth import authenticate # only for users, thoughf
from django.contrib.auth.decorators import user_passes_test

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
    return render(request, "staff_dashboard.html")