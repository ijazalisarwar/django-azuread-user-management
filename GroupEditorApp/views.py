from django.shortcuts import (
    render, 
    redirect,
    HttpResponse,
    HttpResponseRedirect,
    HttpResponsePermanentRedirect
)
from django.urls import reverse
import requests
import json
from GroupEditor.settings import (
    TENANT_ID,
    CLIENT_ID,
    CLIENT_SECRET
)
AD_GET_TOKEN_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
from django.core.cache import cache
from django.contrib import messages
from django.core.paginator import Paginator
import time
# Create your views here.




def home(request):
    if 'tokens' in request.COOKIES:
        return groups(request)
    return render(request,'index.html',{})



def logout_custom(request):
    respone = HttpResponseRedirect(reverse('home_url'))
    print(request.COOKIES)
    # respone.delete_cookie('tokens')
    for cookie in request.COOKIES:
        respone.delete_cookie(cookie)
    print(request.COOKIES)
    return respone


def redirect_uri(request):
    code = request.GET.get('code')
    redirect_uri = (request.build_absolute_uri()).split('?')[0]
    if 'localhost' not in redirect_uri:
        redirect_uri = redirect_uri.replace("http:","https:")


    data_dict = {
        "code":code,
        "redirect_uri": redirect_uri,
        "grant_type":"authorization_code",
        "client_secret":CLIENT_SECRET,
        "client_id":CLIENT_ID,
    }
    respone = requests.post(AD_GET_TOKEN_URL,data_dict)
    data = respone.json()
    data["expires_in"] = int(time.time()) + data["expires_in"] - 5  # 5 sec before refresh it
    respone = render(request, 'success.html', {})
    respone.set_cookie('tokens',data)
    return respone


def redirect_uri_automatic(request):
    code = request.GET.get('code')
    redirect_uri = (request.build_absolute_uri()).split('?')[0]
    if 'localhost' not in redirect_uri:
        redirect_uri = redirect_uri.replace("http:","https:")


    data_dict = {
        "code":code,
        "redirect_uri": redirect_uri,
        "grant_type":"authorization_code",
        "client_secret":CLIENT_SECRET,
        "client_id":CLIENT_ID,
    }
    respone = requests.post(AD_GET_TOKEN_URL,data_dict)
    data = respone.json()
    data["expires_in"] = int(time.time()) + data["expires_in"] - 5  # 5 sec before refresh it
    respone = HttpResponseRedirect(reverse('groups'))
    respone.set_cookie('tokens',data)
    return respone



def refresh_token(request, tokens):
    code = request.GET.get('code')
    redirect_uri = (request.build_absolute_uri()).split('?')[0]
    if 'localhost' not in redirect_uri:
        redirect_uri = redirect_uri.replace("http:","https:")

    body_dict = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": tokens['refresh_token'],
        "grant_type": "refresh_token",
        "scope": "offline_access",
    }
    respone = requests.post(AD_GET_TOKEN_URL,body_dict)
    data = respone.json()
    data["expires_in"] = int(time.time()) + data["expires_in"] - 5  # 5 sec before refresh it
    respone = render(request, 'success.html', {})
    respone.set_cookie('tokens',data)
    return respone


def groups(request):
    groups_list = []
    tokens = ''
    if 'tokens' in request.COOKIES:  tokens = request.COOKIES.get('tokens').replace("'", "\"")
    if tokens: tokens = json.loads(tokens)
    if not tokens:
        return render(request,'index.html',{})

    # if 'expires_in' in tokens and int(tokens["expires_in"]) <= int(time.time()):
    #     tokens = refresh_token(tokens)


    URL = 'https://graph.microsoft.com/v1.0/me/ownedObjects'
    response = requests.get(URL, headers={'Authorization':"Bearer " + tokens["access_token"]})
    if response.status_code == 401 or response.status_code == 403:
        return render(request,'index.html',{})

    groups = response.json()["value"]
    for group in groups:
        if group["@odata.type"] == "#microsoft.graph.group":
            groups_list.append(group)
    return render(request,'groups.html',{"groups_list":groups_list})


def group_detail(request, id):
    group_data = {}
    tokens = ''
    if 'tokens' in request.COOKIES:  tokens = request.COOKIES.get('tokens').replace("'", "\"")
    if tokens: tokens = json.loads(tokens)
    if not tokens:
        return render(request,'index.html',{})
    URL = f'https://graph.microsoft.com/v1.0/groups/{id}'

    response = requests.get(URL, headers={'Authorization':"Bearer " + tokens["access_token"]})
    if response.status_code == 401 or response.status_code == 403:
        return render(request,'index.html',{})
    group_data = response.json()
    return render(request,'group-detail.html',{"group_data":group_data})



def remove_users(request, id):
    group_data = {}
    tokens = ''
    if 'tokens' in request.COOKIES:  tokens = request.COOKIES.get('tokens').replace("'", "\"")
    if tokens: tokens = json.loads(tokens)
    if not tokens:
        return render(request,'index.html',{})
    URL = f'https://graph.microsoft.com/v1.0/groups/{id}/members'

    response = requests.get(URL, headers={'Authorization':"Bearer " + tokens["access_token"]})
    if response.status_code == 401 or response.status_code == 403:
        return render(request,'index.html',{})
    users_data = response.json()["value"]
    return render(request,'remove-users.html',{"users_list":users_data, "group_id":id})


def users_list(request, id):
    group_data = {}
    tokens = ''
    if 'tokens' in request.COOKIES:  tokens = request.COOKIES.get('tokens').replace("'", "\"")
    if tokens: tokens = json.loads(tokens)
    if not tokens:
        return render(request,'index.html',{})
    URL = f'https://graph.microsoft.com/v1.0/groups/{id}/members'
    response = requests.get(URL, headers={'Authorization':"Bearer " + tokens["access_token"]})
    if response.status_code == 401 or response.status_code == 403:
        return render(request,'index.html',{})
    users_data = response.json()["value"]
    return render(request,'users-list.html',{"users_list":users_data, "group_id":id})


def add_users(request, id):
    group_data = {}
    tokens = ''
    if 'tokens' in request.COOKIES:  tokens = request.COOKIES.get('tokens').replace("'", "\"")
    if tokens: tokens = json.loads(tokens)
    if not tokens:
        return render(request,'index.html',{})
    search_string = request.GET.get('search_string')
    if search_string:
        search_string = search_string.lower()
        URL = f'https://graph.microsoft.com/v1.0/users'+ f"?$filter=startswith(displayName,'{search_string}')"
    else:
        URL = f'https://graph.microsoft.com/v1.0/users'
    
    response = requests.get(URL, headers={'Authorization':"Bearer " + tokens["access_token"]})
    if response.status_code == 401 or response.status_code == 403:
        return render(request,'index.html',{})
    
    
    users_data = response.json()["value"]
    paginator = Paginator(users_data, 12)
    page = request.GET.get('page', 1)
    page_obj = paginator.page(page)
    context = {
        'page_obj': page_obj,
        "group_id":id
    }
    return render(request,'add-users.html', context)




def remove_user(request, group_id, user_id):
    group_data = {}
    tokens = ''
    if 'tokens' in request.COOKIES:  tokens = request.COOKIES.get('tokens').replace("'", "\"")
    if tokens: tokens = json.loads(tokens)
    if not tokens:
        return render(request,'index.html',{})
    URL = f'https://graph.microsoft.com/v1.0/groups/{group_id}/members/{user_id}/$ref'

    response = requests.delete(URL, headers={'Authorization':"Bearer " + tokens["access_token"]})
    if response.status_code == 204:
        #success
        messages.info(request,"User removed Successfull.")
        pass
    else:
        # fail
        messages.info(request,"Issue in removing user.")
        pass
    return groups(request)



def add_user(request, group_id, user_id):
    group_data = {}
    tokens = ''
    if 'tokens' in request.COOKIES:  tokens = request.COOKIES.get('tokens').replace("'", "\"")
    if tokens: tokens = json.loads(tokens)
    if not tokens:
        return render(request,'index.html',{})
    URL = f'https://graph.microsoft.com/v1.0/groups/{group_id}/members/$ref'
    json_body = {   
        "@odata.id": f"https://graph.microsoft.com/v1.0/directoryObjects/{user_id}"
    }
    response = requests.post(URL, json=json_body, headers={'Authorization':"Bearer " + tokens["access_token"]})


    if response.status_code == 204:
        #success
        messages.info(request,"User added Successfull.")
        pass
    else:
        # fail
        messages.info(request,"Issue in adding user.")

    return groups(request)




