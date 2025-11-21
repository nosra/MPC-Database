from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from .models import ProPlugin, AlternativePlugin

def home(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render())

def plugins(request):
    pro_plugins = ProPlugin.objects.all()
    alt_plugins = AlternativePlugin.objects.all()
    return render(request, "plugins.html", {
        "pro_plugins": pro_plugins,
        "alt_plugins": alt_plugins,
    })
    
def plugin_detail(request, pk):
    plugin = get_object_or_404(ProPlugin, pk=pk)
    return render(request, "plugin_detail.html", {"plugin": plugin})