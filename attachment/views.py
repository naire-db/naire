from django.core.files.storage import FileSystemStorage
from django.views.decorators.http import require_POST

from attachment.forms import AttachmentForm
from common.models import save_or_400
from .models import Attachment
from common.rest import rest_ok


@require_POST
def upload(request):
    form = AttachmentForm(request.POST, request.FILES)
    if form.is_valid():
        file = request.FILES['file']
        name = file.name
        fs = FileSystemStorage()
        path = fs.save(name, file)
        # TODO: add resp_id
        attachment = Attachment(file=file, name=name)
        save_or_400(attachment)
    return rest_ok()


@require_POST
def download(request):
    pass
