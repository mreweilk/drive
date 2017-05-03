import requests
import httplib2
import os
import re
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader
from django.http import Http404
from django.shortcuts import redirect
from django.contrib.auth import views
from django.contrib.auth import authenticate
import base64
import json
import time


def login(request,template_name,next=None):
    if http_auth_check(request):
        return HttpResponseRedirect(request.GET.get('next'))
    if request.user.is_authenticated():
        return redirect('/drive/')
    if request.GET.get('next') is None or request.GET.get('next') == '' or request.GET.get('next') == '/drive/'+settings.ROOT_ID+'/' or request.GET.get('next') == '/drive/0ADZHgB6IVOHJUk9PVA/':
        template_response = views.login(request,template_name=template_name,extra_context={'next':'/drive/'})
    else:
        if next is not None:
            template_response = views.login(request,template_name=template_name,extra_context={'next':next})
        else:
            template_response = views.login(request,template_name=template_name)
    if next is not None:
        template_response.status_code = 401
        template_response['WWW-Authenticate'] = 'Basic realm="Restricted"'
    return template_response

def is_admin(request):
    return request.user.is_superuser

def http_auth_check(request):
    if request.user.is_authenticated():
        return True
    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(auth[1]).split(':')
                user = authenticate(username=uname, password=passwd)
                if user is not None and user.is_active:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False

def sanitize(filename):
    filter_chars = ['\\','/',':','*','?','"','<','>','|']
    return ''.join(c for c in filename if c not in filter_chars)

def drive_get_service():
    def get_credentials():
        store = oauth2client.file.Storage(settings.CLIENT_SECRET_FILE)
        credentials = store.get()
        return credentials
    
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    return discovery.build('drive', 'v3', http=http)

def latest(request,type):
    if not http_auth_check(request):
        response = redirect('/drive/login')
        if 'all' in type:
            response['Location'] += '?next=/drive/latest/'
        else:
            response['Location'] += '?next=/drive/latest/'+type
        return response
    template = loader.get_template("directory.html")
    service = drive_get_service()
    response = []
    currDir = "latest"
    prevDir = "drive"
    if "all" in type:
        results = service.files().list(
            pageSize=100,orderBy="createdTime desc",
            fields="nextPageToken, files(id, name, mimeType, modifiedTime, size)",
            q="mimeType!='application/vnd.google-apps.folder' and trashed=false",
        ).execute()
    if "1080p" in type:
        results = service.files().list(
            pageSize=100,orderBy="createdTime desc",
            fields="nextPageToken, files(id, name, mimeType, modifiedTime, size)",
            q="mimeType!='application/vnd.google-apps.folder' and name contains '"+type+"' and name contains 'HorribleSubs' and trashed=false",
        ).execute()
    if "720p" in type:
        results = service.files().list(
            pageSize=100,orderBy="createdTime desc",
            fields="nextPageToken, files(id, name, mimeType, modifiedTime, size)",
            q="mimeType!='application/vnd.google-apps.folder' and name contains '"+type+"' and name contains 'HorribleSubs' and trashed=false",
        ).execute()
    if "SD" in type:
        results = service.files().list(
            pageSize=100,orderBy="createdTime desc",
            fields="nextPageToken, files(id, name, mimeType, modifiedTime, size)",
            q="mimeType!='application/vnd.google-apps.folder' and (name contains '480p' or name contains '360p') and name contains 'HorribleSubs' and trashed=false",
        ).execute()
    items = results.get('files', [])

    if items:
        for item in items:
            modTime = time.strptime(item['modifiedTime'],"%Y-%m-%dT%H:%M:%S.%fZ")
            date = time.strftime("%A, %B %d, %Y %H:%M %p",modTime)
            imagelink = item['thumbnailLink'][:-5] if item['name'].endswith(settings.IMAGE_FILES) else None
            response.append({
                    "date":"{0:>38}".format(date),
                    "type":("{0:>19}".format("<dir>") if "application/vnd.google-apps.folder" in item['mimeType'] else "{0:>19}".format(item['size'])),
                    "id":item['id'],
                    "name":item['name'],
                    "download":(False if "application/vnd.google-apps.folder" in item['mimeType'] else True),
                    "video":(True if item['name'].endswith(settings.VIDEO_FILES) else False),
                    "image":(True if (item['name'].endswith(settings.IMAGE_FILES) and imagelink is not None) else False),
                    "imagelink":(imagelink+"=s9999" if imagelink is not None else None)
            })

    context = {
        "currDir": currDir,
        "prevDir": prevDir,
        "items": response,
        "admin":is_admin(request)
    }
    return HttpResponse(template.render(context, request))

def directory(request,directory):
    if not http_auth_check(request):
        response = redirect('/drive/login')
        response['Location'] += '?next=/drive/'+directory+'/'
        return response
    template = loader.get_template("directory.html")
    service = drive_get_service()
    response = []
    currDir = "drive"
    prevDir = False
    if settings.ROOT_ID not in directory:
        try:
            results = service.files().get(fileId=directory,fields="parents,name,mimeType",).execute()
        except:
            raise Http404
        res = results.get('parents', [])
        if not res:
            raise Http404
        if settings.ROOT_ID in results['parents'][0]:
            prevDir = "drive"
        else:
            prevDir = "drive/"+results['parents'][0]
        if "application/vnd.google-apps.folder" not in results['mimeType']:
            raise Http404
        currDir = results['name']

    items = []
    results = service.files().list(
        pageSize=1000,orderBy="folder,name",
        fields="nextPageToken, files(id, name, mimeType, modifiedTime, size, thumbnailLink, shared)",
        q="'"+directory+"' in parents and trashed=false",
    ).execute()
    res = results.get('files', [])
    for item in res:
        if item['shared']:
            items.append(item)
    while results.get('nextPageToken') is not None:
        results = service.files().list(pageToken=results.get('nextPageToken'),
            pageSize=1000,orderBy="folder,name",
            fields="nextPageToken, files(id, name, mimeType, modifiedTime, size, thumbnailLink, shared)",
            q="'"+directory+"' in parents and trashed=false",
        ).execute()
        res = results.get('files', [])
        for item in res:
            if item['shared']:
                items.append(item)
    json_data = []
    if items:
        for item in items:
            if request.method == 'GET' and 'json'in request.GET and "application/vnd.google-apps.folder" not in item['mimeType']:
                json_data.append(settings.SITE_URL+item['id']+"/"+item['name'])
            else:    
                modTime = time.strptime(item['modifiedTime'],"%Y-%m-%dT%H:%M:%S.%fZ")
                date = time.strftime("%A, %B %d, %Y %H:%M %p",modTime)
                imagelink = item['thumbnailLink'][:-5] if item['name'].endswith(settings.IMAGE_FILES) else None
                response.append({
                        "date":"{0:>38}".format(date),
                        "type":("{0:>19}".format("<dir>") if "application/vnd.google-apps.folder" in item['mimeType'] else "{0:>19}".format(item['size'])),
                        "id":item['id'],
                        "name":item['name'],
                        "download":(False if "application/vnd.google-apps.folder" in item['mimeType'] else True),
                        "video":(True if item['name'].endswith(settings.VIDEO_FILES) else False),
                        "audio":(True if item['name'].endswith(settings.AUDIO_FILES) else False),
                        "image":(True if (item['name'].endswith(settings.IMAGE_FILES) and imagelink is not None) else False),
                        "imagelink":(imagelink+"=s9999#.jpg" if imagelink is not None else None)
                })
    if request.method == 'GET' and 'json' in request.GET:
        json_data = {sanitize(currDir):json_data}
        return HttpResponse(json.JSONEncoder().encode(json_data))
    else:
        context = {
            "currDir": currDir,
            "prevDir": prevDir,
            "items": response,
            "admin":is_admin(request)
        }
        return HttpResponse(template.render(context, request))

def download(request,fileId,fileName):
    if not http_auth_check(request):
        return login(request,template_name='login.html',next='/drive/'+fileId+'/'+fileName)
    service = drive_get_service()
    try:
        results = service.files().get(fileId=fileId,fields="mimeType",).execute()
        if "application/vnd.google-apps.folder" in results['mimeType']:
            raise Http404
    except:
        raise Http404
    s = requests.Session()
    req = s.get("https://drive.google.com/uc?export=download&id="+fileId,allow_redirects=False)
    if req.headers.get('Location') is None:
        m = re.search(r'download&amp;confirm=(.*)&amp;id',req.text)
        try:
            confirmationId = m.group(1)
        except AttributeError:
            raise Http404
        req = s.get("https://drive.google.com/uc?export=download&id="+
                    fileId+"&confirm="+confirmationId,allow_redirects=False)
    return HttpResponseRedirect(req.headers['Location'])
