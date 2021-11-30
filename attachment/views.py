from django.core.exceptions import PermissionDenied
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST, require_safe

from attachment.forms import AttachmentForm, ImageForm
from attachment.models import Attachment, Image
from common.deco import check_logged_in
from naire import settings
from common.rest import rest_fail, rest_data


def save_form_or_400(form):
    if form.is_valid():
        try:
            return form.save()
        except ValueError:
            raise PermissionDenied


@require_POST
def upload_file(request):
    form = AttachmentForm(request.POST, request.FILES)
    obj = save_form_or_400(form)
    if obj:
        obj.name = obj.file.path.split('/')[-1]
        obj.save()
        return rest_data(obj.id)
    # TODO: add resp_id after resp submit
    if settings.DEBUG:
        for field in form:
            print('Field Error:', field.name, field.errors)
    return HttpResponse(status=422)  # Unprocessable Entity


@require_safe
@check_logged_in
def download_file(request, fid):
    # TODO: check response's authority
    attachment = get_object_or_404(Attachment, id=fid)
    return FileResponse(open(attachment.file.path, 'rb'))


@require_POST
def upload_image(request):
    form = ImageForm(request.POST, request.FILES)
    obj = save_form_or_400(form)
    if obj:
        obj.name = obj.image.path.split('/')[-1]
        obj.save()
        return rest_data(obj.id)
    # TODO: add form_id after form submit
    if settings.DEBUG:
        for field in form:
            print('Field Error:', field.name, field.errors)
    return HttpResponse(status=415)  # Unsupported Media Type


@require_safe
@check_logged_in
def download_image(request, image_id):
    # TODO: check response's authority
    obj = get_object_or_404(Image, id=image_id)
    return FileResponse(open(obj.image.path, 'rb'))
