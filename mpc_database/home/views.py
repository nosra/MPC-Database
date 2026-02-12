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

from .models import ProPlugin, AlternativePlugin, CATEGORIES, Rating, Category, Subcategory, PluginSuggestion, AudioDemo
from .forms import StaffPluginSubmission, SuggestionForm

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
        # is the active_category a parent category slug?
        if Category.objects.filter(slug=active_category).exists():
            active_parent_slug = active_category
            plugins_qs = plugins_qs.filter(
                subcategories__parent__slug=active_category
            ).distinct()

        # otherwise it's a subcategory slug
        else:
            sub = Subcategory.objects.filter(slug=active_category).first()
            if sub:
                active_parent_slug = sub.parent.slug
                plugins_qs = plugins_qs.filter(
                    subcategories__slug=active_category
                ).distinct()


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

@login_required
def profile_view(request):
    # handle the form submission
    if request.method == 'POST':
        form = SuggestionForm(request.POST)
        if form.is_valid():
            suggestion = form.save(commit=False)
            suggestion.submitter = request.user # attach current user
            suggestion.save()
            return redirect('profile') # redirect to same page to clear form
    else:
        form = SuggestionForm()

    # fetch user's history
    user_suggestions = PluginSuggestion.objects.filter(
        submitter=request.user
    ).order_by('-date_suggested')

    context = {
        'form': form,
        'user_suggestions': user_suggestions
    }
    return render(request, 'profile.html', context)

# ---------
# submissions routers
# ---------
def staff_check(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(staff_check, login_url="login")
def staff_dashboard(request):
    # handling rejecting a plugin
    if request.method == "POST" and "reject_suggestion" in request.POST:
        s_id = request.POST.get("suggestion_id")
        PluginSuggestion.objects.filter(pk=s_id).update(status='REJECTED')
        messages.info(request, "Suggestion rejected.")
        return redirect("staff_dashboard")

    # handling a plugin submission from a staff member
    if request.method == "POST" and "submit_plugin" in request.POST:
        form = StaffPluginSubmission(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data

            common = dict(
                submitter=request.user,
                name=data["plugin_name"],
                date_released=data["date_released"],
                price=data["price"],
                description=data["description"],
                size=data["size"],
                download_link=data["download_link"],
                image=data.get("image"),
            )

            created_plugin = None
            is_pro = False

            if data["plugin_type"] == "PRO":
                plugin = ProPlugin.objects.create(**common)
                plugin.subcategories.set(data["subcategory"])
                created_plugin = plugin
                is_pro = True
            else:
                alt = AlternativePlugin.objects.create(**common)
                alt.subcategories.set(data["subcategory"])
                for pro in data.get("link_to_pro_plugins", []):
                    pro.alternatives.add(alt)
                created_plugin = plugin
                is_pro = False # pedantic

            for i in range(1, 4):
                audio_file = data.get(f"audio_demo_{i}")
                title = data.get(f"demo_title_{i}")

                if audio_file:
                    demo = AudioDemo(
                        audio_file=audio_file,
                        title=title if title else audio_file.name # fallback to filename
                    )
                    # Link to the correct parent
                    if is_pro:
                        demo.pro_plugin = created_plugin
                    else:
                        demo.alt_plugin = created_plugin
                    
                    demo.save()
            
            # checking if the comes from a submission
            sid = data.get("suggestion_id")
            if sid:
                PluginSuggestion.objects.filter(pk=sid).update(status='APPROVED')

            messages.success(request, "Plugin submitted successfully!")
            return redirect("staff_dashboard")
    else:
        form = StaffPluginSubmission()

    # fetching peding suggestions from the UI
    suggestions = PluginSuggestion.objects.filter(status='PENDING').order_by('date_suggested')

    # fetching pro and alt plugins
    my_pro_plugins = ProPlugin.objects.filter(submitter=request.user).order_by('-date_released')
    my_alt_plugins = AlternativePlugin.objects.filter(submitter=request.user).order_by('-date_released')

    return render(request, "staff_dashboard.html", {
        "form": form,
        "suggestions": suggestions,
        "my_pro_plugins": my_pro_plugins,
        "my_alt_plugins": my_alt_plugins,
    })

@user_passes_test(staff_check, login_url="login")
@require_POST
def delete_plugin(request):
    plugin_id = request.POST.get('plugin_id')
    plugin_type = request.POST.get('plugin_type')
    
    if plugin_type == 'PRO':
        model = ProPlugin
    elif plugin_type == 'ALT':
        model = AlternativePlugin
    else:
        messages.error(request, "Invalid plugin type.")
        return redirect("staff_dashboard")
        
    plugin = get_object_or_404(model, pk=plugin_id)
    
    # security check to ensure they own the plugin
    # this can be removed if we decide later down the line to allow staff members to delete any plugin
    if plugin.submitter != request.user and not request.user.is_superuser:
        messages.error(request, "You can only delete plugins you submitted.")
        return redirect("staff_dashboard")

    # perform deletion
    name = plugin.name
    plugin.delete()
    messages.success(request, f"Deleted '{name}' successfully.")
    
    return redirect("staff_dashboard")

def about(request):
    return render(request, "about.html")

def search_plugins(request):
    query = (request.GET.get('q') or '').strip()
    results = []

    if len(query) > 1:
        # limit + prefetch to avoid N+1 queries
        alts = AlternativePlugin.objects.filter(name__icontains=query).prefetch_related('subcategories')[:3]
        for item in alts:
            # build a readable category string from subcategories
            sub_names = list(item.subcategories.order_by('parent__name', 'name').values_list('name', flat=True))
            category_display = ", ".join(sub_names) if sub_names else "Uncategorized"

            results.append({
                'name': item.name,
                'category': category_display,
                'type': 'Free',
                'image': item.image_url,
                'url': reverse('alt_plugin_detail', args=[item.pk])
            })

        pros = ProPlugin.objects.filter(name__icontains=query).prefetch_related('subcategories')[:3]
        for item in pros:
            sub_names = list(item.subcategories.order_by('parent__name', 'name').values_list('name', flat=True))
            category_display = ", ".join(sub_names) if sub_names else "Uncategorized"

            results.append({
                'name': item.name,
                'category': category_display,
                'type': 'Pro/Paid',
                'image': item.image_url,
                'url': reverse('plugin_detail', args=[item.pk])
            })

    return JsonResponse({'results': results})
