import os

from django.http import Http404, HttpResponseForbidden
from django.views.decorators.http import require_POST

from attachment.forms import AttachmentForm
from naire import settings
from common.rest import rest_ok, rest_fail, rest_data, acquire_json


@require_POST
def upload_file(request):
    form = AttachmentForm(request.POST, request.FILES)
    if form.is_valid():
        try:
            attachment = form.save()
        except ValueError:
            return HttpResponseForbidden()
        print(attachment.file.url)
        return rest_data(attachment.id)
    if settings.DEBUG:
        for field in form:
            print('Field Error:', field.name, field.errors)
    return rest_fail()


@acquire_json
def download_file(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb'):
            pass
        # return rest_ok()
    raise Http404
