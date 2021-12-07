from django.core.exceptions import BadRequest
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST, require_safe

from common.deco import check_logged_in
from common.log import logger
from common.rest import rest_data

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
    file = request.FILES.get('file')
    if file.size > 20 * 1024 * 1024:
        raise BadRequest
    attachment: Attachment = save_form_or_400(form)
    attachment.set_filename(file.name)
    attachment.save()
    return rest_data(attachment.token)
    # TODO: add resp id


@require_safe
@check_logged_in
def get_file(request, token):
    # TODO: check response's authority
    attachment = get_object_or_404(Attachment, token=token)
    return FileResponse(attachment.file, filename=attachment.filename)


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
