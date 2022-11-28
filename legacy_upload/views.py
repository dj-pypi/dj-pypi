from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView

from legacy_upload.forms import LegacyUploadForm


@method_decorator(csrf_exempt, name="dispatch")
class LegacyUploadView(LoginRequiredMixin, CreateView):
    form_class = LegacyUploadForm
    template_name = "legacy_upload/upload_form.html"
    raise_exception = True

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["request"] = self.request
        return form_kwargs

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponse(status=201)

    def form_invalid(self, form):
        return HttpResponse(form.errors.as_text(), status=400, content_type="text/plain; charset=utf-8")

    def get_success_url(self):
        return "/"
