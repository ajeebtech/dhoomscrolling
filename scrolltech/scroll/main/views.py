from django.shortcuts import render
import selenium
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import UserInterest

def interest_selection(request):
    return render(request, "interests.html")

@login_required
def select_interests(request):
    if request.method == "POST":
        data = request.POST.getlist("interests")  # Get interests list
        if len(data) > 3:
            return JsonResponse({"error": "You can select only 3 interests."}, status=400)

        user_interests, created = UserInterest.objects.get_or_create(user=request.user)
        user_interests.interests = data
        user_interests.save()
        return JsonResponse({"message": "Interests saved!"})

    return render(request, "select_interests.html")

@login_required
def select_voice(request):
    if request.method == "POST":
        voice = request.POST.get("voice")
        user_interests = UserInterest.objects.get(user=request.user)
        user_interests.voice = voice
        user_interests.save()
        return JsonResponse({"message": "Voice saved!"})

    return render(request, "select_voice.html")

@login_required
def study_topic(request):
    user_interests = UserInterest.objects.get(user=request.user)
    return render(request, "study_topic.html", {"interests": user_interests.interests})
