from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.db.models import Q, Avg
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.http import require_POST
from django.contrib.contenttypes.models import ContentType

from .models import ProPlugin, AlternativePlugin, CATEGORIES, Rating, Category, Subcategory
from .forms import StaffPluginSubmission

import json

def home(request):
    return render(request, 'home.html')
# ---------
# plugins routers
# ---------

def plugins(request):
    tab = request.GET.get("tab", "pro")
    search_query = (request.GET.get("q") or "").strip()

    # filter by slug field
    active_category = request.GET.get('category')
    categories = Category.objects.prefetch_related('subcategories').all()

    # parent slug for highlighting, purely visual
    active_parent_slug = None

    # figure out which list we're showing
    if tab == "alt":
        plugins_qs = AlternativePlugin.objects.all()
        active_tab = "alt"
    else:
        plugins_qs = ProPlugin.objects.all()
        active_tab = "pro"

    # validate & apply category filter
    if active_category:
        # is the active_category a parent
        if Category.objects.filter(slug=active_category).exists():
            active_parent_slug = active_category
            plugins_qs = plugins_qs.filter(subcategory__parent__slug=active_category)
            
        # is it a subcategory?
        else:
            # find the subcategory object to get its parent
            sub = Subcategory.objects.filter(slug=active_category).first()
            if sub:
                active_parent_slug = sub.parent.slug
                plugins_qs = plugins_qs.filter(subcategory__slug=active_category)
    # apply search filter if there's a query
    if search_query:
        plugins_qs = plugins_qs.filter(
            Q(name__icontains=search_query)
            # other filters can be requested too
            # | Q(description__icontains=search_query)
            # | Q(company__icontains=search_query)
        )

    context = {
        "active_parent_slug": active_parent_slug,
        "plugins": plugins_qs,
        "categories": categories,
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
    
    # check if user has already rated this
    user_rating = 0
    if request.user.is_authenticated:
        rating_obj = Rating.objects.filter(
            user=request.user,
            content_type=ContentType.objects.get_for_model(plugin),
            object_id=plugin.id
        ).first()
        if rating_obj:
            user_rating = rating_obj.score

    context = {
        "plugin": plugin,
        "user_rating": user_rating,
        "plugin_type": "pro" # helper for the JS fetch URL
    }
    return render(request, "plugin_detail.html", context)


def alt_plugin_detail(request, pk):
    plugin = get_object_or_404(AlternativePlugin, pk=pk)

    # check if user has already rated this
    user_rating = 0
    if request.user.is_authenticated:
        rating_obj = Rating.objects.filter(
            user=request.user,
            content_type=ContentType.objects.get_for_model(plugin),
            object_id=plugin.id
        ).first()
        if rating_obj:
            user_rating = rating_obj.score

    context = {
        "plugin": plugin,
        "user_rating": user_rating,
        "plugin_type": "alt" 
    }
    return render(request, 'alt_plugin_detail.html', context)

# ---------
# rating logic
# ---------

@login_required
@require_POST
def rate_plugin(request, plugin_type, plugin_id):
    # parsing the json
    try:
        data = json.loads(request.body)
        score = float(data.get('score'))
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid score'}, status=400)

    if score < 0.5 or score > 5.0:
        return JsonResponse({'error': 'Score must be between 1 and 5'}, status=400)

    # resolving model
    if plugin_type == 'pro':
        model_class = ProPlugin
    elif plugin_type == 'alt':
        model_class = AlternativePlugin
    else:
        return JsonResponse({'error': 'Invalid plugin type'}, status=400)

    plugin = get_object_or_404(model_class, pk=plugin_id)

    # create or update rating
    Rating.objects.update_or_create(
        user=request.user,
        content_type=ContentType.objects.get_for_model(plugin),
        object_id=plugin.id,
        defaults={'score': score}
    )

    # recalculate average on the model 
    if hasattr(plugin, 'calculate_average_rating'):
        plugin.calculate_average_rating()
    
    return JsonResponse({'success': True, 'new_average': plugin.rating})


# ---------
# user routers
# ---------

def profile(request):
    return render(request, 'profile.html')

# ---------
# submissions routers
# ---------
def staff_check(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(staff_check, login_url="login")
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
        # search free alternatives
        alts = AlternativePlugin.objects.filter(name__icontains=query)[:3] # only going up to 3 plugins
        for item in alts:
            results.append({
                'name': item.name,
                'category': item.get_category_display(),
                'type': 'Free',
                'image': item.image_url,
                'url': reverse('alt_plugin_detail', args=[item.pk]) 
            })

        # search pro plugins
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