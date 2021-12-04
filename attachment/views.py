from django.core.exceptions import PermissionDenied, BadRequest
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST, require_safe

from common.deco import check_logged_in
from common.log import logger
from common.rest import rest_data

from naire import settings

from attachment.forms import AttachmentForm, ImageForm
from attachment.models import Attachment, Image


def save_form_or_400(form):
    if form.is_valid():
        try:
            return form.save(commit=False)
        except Exception as e:
            logger.error(f'attachment form: {type(e).__name__} {e}')
            raise BadRequest
    else:
        raise BadRequest


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
    file = request.FILES.get('file')
    if file.size > 10 * 1024 * 1024:
        raise BadRequest
    image: Image = save_form_or_400(form)
    image.set_filename(file.name)
    image.save()
    return rest_data(image.id)
    # TODO: add form_id after form submit


@require_safe
def get_image(request, image_id):
    # TODO: check response's authority
    image = get_object_or_404(Image, id=image_id)
    return FileResponse(image.file, filename=image.filename)
