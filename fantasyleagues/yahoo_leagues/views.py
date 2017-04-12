from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse
from pprint import pprint
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template.context_processors import csrf

from yahoo_leagues.models import UserModel

import urllib, urllib2, base64
import urlparse
import time
import oauth2 as oauth
import json
import re
import requests, json


def apicall(request, api):
    header = {
        'Authorization': 'Bearer %s'%request.session['access_token']
    }
    r = requests.get(api,headers=header)

    print r.text

    if r.status_code != 200:
        print "REFRESHING ACCESS TOKEN"
        t_url = 'https://api.login.yahoo.com/oauth2/get_token'
        base64string = base64.encodestring('%s:%s' % (settings.YAHOO_CONSUMER_KEY, settings.YAHOO_CONSUMER_SECRET)).replace('\n', '') 
        data = {
                'client_id': settings.YAHOO_CONSUMER_KEY,
                'client_secret': settings.YAHOO_CONSUMER_SECRET,
                'grant_type': 'refresh_token',
                'redirect_uri': 'http://'+settings.SITE_URL+reverse('auth'), 
                'refresh_token': request.session['refresh_token']
            }
        header = {
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", 
                "Authorization": "Basic %s" % base64string, 
                "Content-Type": "application/x-www-form-urlencoded", # Grant type
        }
        q = ''

        for key in data.keys():
            q = q+key+"="+data[key]+'&'

        q = q[:-1]

        r = requests.post(t_url, data=q, headers=header)

        r = json.loads(r.text)

        print r

        for key in r.keys():
            request.session[key] = r[key]

        header = {
            'Authorization': 'Bearer %s'%request.session['access_token']
        }

    r = requests.get(api,headers=header)

    print r

    return json.loads(r.text)

class YahooAuth(View):

    def get(self, request):

        param = {
            'client_id': settings.YAHOO_CONSUMER_KEY,
            'redirect_uri': 'http://'+settings.SITE_URL+reverse('auth'), 
            'response_type': 'code', 
            'state': 'state', 
        }
        t_url = "https://api.login.yahoo.com/oauth2/request_auth?"

        y_login_url =  t_url + urllib.urlencode(param)


        print y_login_url  #YAHOO login url - NOT local LoginView

        return HttpResponseRedirect(y_login_url)


class LoginView(View):

    template_name = "login.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        for key in request.session.keys():
            del request.session[key]
        return HttpResponseRedirect(reverse('yahoo_auth'))

class AuthView(View):

    def get(self, request):

        t_url = "https://api.login.yahoo.com/oauth2/get_token"
        base64string = base64.encodestring('%s:%s' % (settings.YAHOO_CONSUMER_KEY, settings.YAHOO_CONSUMER_SECRET)).replace('\n', '') 

        data = {
                'client_id': settings.YAHOO_CONSUMER_KEY,
                'client_secret': settings.YAHOO_CONSUMER_SECRET,
                'grant_type': 'authorization_code',
                'redirect_uri': 'http://'+settings.SITE_URL+reverse('auth'), 
                'code': request.GET['code']
            }
        header = {
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", 
                "Authorization": "Basic %s" % base64string, 
                "Content-Type": "application/x-www-form-urlencoded", # Grant type
        }

        print data
        print header

        q = ''

        for key in data.keys():
            q = q+key+"="+data[key]+'&'
        q = q[:-1]

        print q

        # req = urllib2.Request(t_url, urllib.urlencode(data), header) 
        r = requests.post(t_url, data=q, headers=header)

        print r

        r = json.loads(r.text)

        print r

        for key in r.keys():
            request.session[key] = r[key]

        print request.session

        # result = urllib2.urlopen(req).read()

        return HttpResponseRedirect(reverse('success'))

class HomeView(View):

    def get(self, request):
       return render(request, 'home.html', {
        
        })

class SuccessView(View):

    def get(self, request):

        if request.session['access_token'] is None:
            return HttpResponseRedirect('home')

        profile_api = "https://social.yahooapis.com/v1/user/%s/profile?format=json"%request.session['xoauth_yahoo_guid']
        data = apicall(request, profile_api)

        print data

        users = UserModel.objects.filter(user_id=request.session['xoauth_yahoo_guid'])
        if len(users) == 0:
            UserModel(
                nickname=data['profile']['nickname'], 
                imageurl=data['profile']['image']['imageUrl'], 
                user_id=request.session['xoauth_yahoo_guid']
                ).save()

        return render(request, 'success.html', {
            'data': data['profile']
            })

class ShowLeague(View):

    def get(self, request):

        if request.session['access_token'] is None:
            return HttpResponseRedirect('home')

        league_api = "https://fantasysports.yahooapis.com/fantasy/v2/game/nfl?format=json"
        data = apicall(request, league_api)

        print data

        return render(request, 'show_league.html', {
            'data': data['fantasy_content']['game']
            })
