from django.http import HttpResponseForbidden, FileResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST, require_safe

from attachment.forms import AttachmentForm
from attachment.models import Attachment
from common.deco import check_logged_in
from naire import settings
from common.rest import rest_ok, rest_fail, rest_data


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


@require_safe
@check_logged_in
def download_file(request, fid):
    # TODO: check response's authority
    attachment = get_object_or_404(Attachment, id=fid)
    return FileResponse(open(attachment.file.path, 'rb'))

