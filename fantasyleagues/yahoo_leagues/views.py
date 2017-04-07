from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect

# Create your views here

class LoginView(View):

    template_name = "login.html"
    client_id = "dj0yJmk9MXdwMzRJbUFJYldDJmQ9WVdrOWIyMDVTRTlFTjJNbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmeD01Yg--"
    client_secret = "844b220df7d9cc93630a1bf2d7f65bde4741fc1a"    
    redirect_uri = "http://ec2-54-202-91-106.us-west-2.compute.amazonaws.com/success/"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        url = "https://api.login.yahoo.com/oauth2/request_auth?client_id="+self.client_id+"&redirect_uri="+self.redirect_uri+"&response_type=token&language=en-us"
        return HttpResponseRedirect(url)

class SuccessView(View):

    template_name = "success.html"

    def get(self, request):
        print request
        return render(request, self.template_name)

