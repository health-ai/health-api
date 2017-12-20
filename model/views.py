from django.contrib.auth.models import User, Group
from .models import Submission
from rest_framework import viewsets, renderers
from rest_framework.decorators import list_route
from .serializers import UserSerializer, SubmissionSerializer
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from forms import SubmissionForm
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import get_user_model # If used custom user model
from rest_framework.generics import CreateAPIView
from rest_framework import permissions, status
from django.contrib.auth.decorators import login_required

import json
import math

class CreateUserView(CreateAPIView):
    model = get_user_model()
    permission_classes = [
        permissions.AllowAny # Or anon users can't register
    ]
    serializer_class = UserSerializer
    
# class UserViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = User.objects.all().order_by('-date_joined')
#     serializer_class = UserSerializer


class SubmissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    parser_classes = (MultiPartParser, FormParser,)
    serializer_class = SubmissionSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.status = 'r'
            instance.save()
            return Response(status=status.HTTP_200_OK)
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        if not self.request.user.is_superuser:
            return Submission.objects.filter(user=self.request.user).exclude(status='r')
        return Submission.objects.all()
        

    def perform_create(self, serializer):
        serializer.save(video=self.request.data.get('video'), user=self.request.user)

    @list_route()
    def dequeue(self, request, *args, **kwargs):
         queue = Submission.objects.all().filter(status='s')
         if queue.count() == 0:
             return Response(None)
         sub = queue[0]
         sub.status = 'p'
#         sub.save()
         return Response(self.serializer_class(sub).data)
     
    def patch(self, request, *args, **kwargs):
        return self.update_partial(request, *args, **kwargs)

from django.http import Http404
from django.shortcuts import render

@login_required(login_url='/api/auth/login/')
def index(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SubmissionForm(request.POST, request.FILES)
        # check whether it's valid:
        if form.is_valid():
            sub = form.save(commit=False)
            sub.user = request.user
            sub.save()

            return redirect(sub)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SubmissionForm()

    return render(request, 'index.html', {'form': form})

def analysis(request, sid):
    sub = get_object_or_404(Submission, pk=sid)
    if not sub.analysis:
        return render(request, 'wait.html')

    analysis = json.loads(sub.analysis)

    if analysis['pose'] == 'DTL':
        analysis['backbend_score'] = max(min(100, 101 - abs(analysis['hipshoear_angle'])), 50)
        analysis['alignment_score'] = max(min(100, 105 - analysis['alignment_score']), 50)
    else:
        analysis['shoulder_score'] = max(min(100, 110 - 5* abs(analysis['shoulder_tilt'] - 17)), 50)
        penalty = 0
        penalty += (analysis['rhip_angle'] - 1 > analysis['lhip_angle']) * 10
        penalty += (180 - analysis['lhip_angle'])/2
        analysis['alignment_score'] = max(min(100,105 - penalty), 50) # max(min(100, 110 - analysis['alignment_score']), 50)

    return render(request, 'analysis.html', {'analysis': analysis, 'video': sub.processed_video })
    
def simulate(request, sid):
    sub = get_object_or_404(Submission, pk=sid)
    sub.status = 'd'
    sub.processed_video = sub.video
    sub.analysis = "{\"pose\": \"FO\", \"rhip_angle\": 12.958002002161948, \"alignment_score\": 6.4420569786243504, \"shoulder_tilt\": 26.314325005127188, \"version\": \"0.1a\", \"hipshoear_angle\": 15.629765817319992, \"lhip_angle\": 165.33442919699203}"
    sub.save()
    return redirect(sub)
