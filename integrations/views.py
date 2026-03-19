from django.shortcuts import render

# Create your views here.

def integrations(request):
    return render(request, 'integrations/integrations.html', {'title': 'Integrations'})

