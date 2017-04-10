from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse
from pprint import pprint
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template.context_processors import csrf

import urllib2
import urlparse
import time
import oauth2 as oauth
import json
import re


class YahooAuth(View):
    def get_authorization_url(self, request):

        # URL to where we will redirect to
        redirect_url = 'http://'+settings.SITE_URL + reverse('auth')

        # set the api URL
        url = 'https://api.login.yahoo.com/oauth/v2/get_request_token'

        # required params for yahoo
        params = {
            'oauth_callback': redirect_url,
            'oauth_timestamp': str(int(time.time())),
            'oauth_nonce': unicode(csrf(request)['csrf_token']),
            'oauth_version': '1.0',
            'xoauth_lang_pref': 'en-us'
        }

        # create the consumer
        consumer = oauth.Consumer(key=settings.YAHOO_CONSUMER_KEY, secret=settings.YAHOO_CONSUMER_SECRET)

        # create the request
        req = oauth.Request(method='GET', url=url, parameters=params)

        # sign the request
        signature_method = oauth.SignatureMethod_PLAINTEXT()
        req.sign_request(signature_method, consumer, None)

        # get the request token from yahoo
        print req.to_url()
        response = urllib2.urlopen(req.to_url()).read()

        # parse the response
        params = urlparse.parse_qs(response)

        # store the returned values
        request.session['yahoo_oauth_token'] = params['oauth_token'][0]
        request.session['yahoo_oauth_token_secret'] = params['oauth_token_secret'][0]

        # get the authorization URL
        url = 'https://api.login.yahoo.com/oauth/v2/request_auth?oauth_token=' + params['oauth_token'][0]

        print "AUTH URL"
        print url

        return url    

    def get(self, request):
        return HttpResponseRedirect(self.get_authorization_url(request))

class LoginView(View):

    template_name = "login.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return HttpResponseRedirect(reverse('yahoo_auth'))

class AuthView(View):

    def verify(self, request):

        # ensure we have a session token and the token value is the same as what yahoo returned
        if 'yahoo_oauth_token' not in request.session \
           or 'oauth_token' not in request.GET \
           or 'oauth_verifier' not in request.GET \
           or request.session['yahoo_oauth_token'] != request.GET['oauth_token']:
            return False
        else:
            return True

    def get(self, request):
        if self.verify(request):
            data = self.get_user_data(request)
            print data
            return render(request, 'success.html', {
                'data': data
            })
        else:
            return HttpResponseRedirect(reverse('home'))

    def get_user_data(self, request):

        data = {}

        print "get_user_data called"

        # if we don't have a token yet, get one now
        if 'yahoo_access_token' not in request.session:

            print 'yahoo_access_token not in request.session'

            # set the api URL
            url = 'https://api.login.yahoo.com/oauth/v2/get_token'

            # required params for yahoo
            params = {
                'oauth_timestamp': str(int(time.time())),
                'oauth_nonce': unicode(csrf(request)['csrf_token']),
                'oauth_version': '1.0',
                'xoauth_lang_pref': 'en-us',
                'oauth_verifier': request.GET['oauth_verifier']
            }

            # create the consumer and token
            consumer = oauth.Consumer(key=settings.YAHOO_CONSUMER_KEY, secret=settings.YAHOO_CONSUMER_SECRET)
            token = oauth.Token(key=request.session['yahoo_oauth_token'], secret=request.session['yahoo_oauth_token_secret'])

            # create the request
            req = oauth.Request(method='GET', url=url, parameters=params)

            # sign the request
            signature_method = oauth.SignatureMethod_PLAINTEXT()
            req.sign_request(signature_method, consumer, token)

            # get the request token from yahoo
            response = urllib2.urlopen(req.to_url()).read()

            # parse the response
            params = urlparse.parse_qs(response)

            # store the returned values
            request.session['yahoo_guid'] = params['xoauth_yahoo_guid'][0]
            request.session['yahoo_access_token'] = params['oauth_token'][0]
            request.session['yahoo_access_token_secret'] = params['oauth_token_secret'][0]

        # set the url using the user id
        url = 'https://social.yahooapis.com/v1/user/%s/profile?format=json' % request.session['yahoo_guid']

        print url

        consumer = oauth.Consumer(key=settings.YAHOO_CONSUMER_KEY, secret=settings.YAHOO_CONSUMER_SECRET)
        token = oauth.Token(key=request.session['yahoo_access_token'], secret=request.session['yahoo_access_token_secret'])

        # get the user's data from yahoo
        client = oauth.Client(consumer, token)
        response, content = client.request(url)

        print response

        # grab the profile from the response
        user = json.loads(content)['profile']

        print user

        # split the name
        full_name = user['nickname'].split(' ', 1)

        # get the user's info
        data['user_id'] = user['guid']
        data['username'] = re.sub('[^0-9a-zA-Z]+', '', user['nickname']).lower()
        #data['email'] = user['emails'][0]['handle'] if 'handle' in user['emails'][0] else ''
        data['full_name'] = user['nickname']
        data['first_name'] = full_name[0] if len(full_name) > 0 else ''
        data['last_name'] = full_name[1] if len(full_name) >= 2 else ''
        #data['timezone'] = user['timeZone']
        data['picture'] = user['image']['imageUrl']

        return data

class HomeView(View):

    def get(self, request):
       return HttpResponse("<h1> Home </h1>")
