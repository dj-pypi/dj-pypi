import mimetypes
from pathlib import Path

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q, QuerySet
from django.http import FileResponse, Http404, HttpRequest, HttpResponseBase, HttpResponseNotModified
from django.shortcuts import get_object_or_404
from django.utils.http import http_date
from django.views import View
from django.views.generic import TemplateView
from django.views.static import was_modified_since

from legacy_upload.models import LegacyUpload
from projects.models import Project
from token_auth.models import AuthToken


class ProjectIndex(TemplateView):
    """List all visible projects."""

    template_name = "simple_index/project_index.html"

    def get_visible_projects(self) -> QuerySet[Project]:
        if isinstance(self.request.user, AuthToken):
            project_filter = Q(is_public=True) | Q(
                pk__in=self.request.user.projectpermission_set.filter(
                    permissions__content_type__app_label="projects", permissions__codename="view_project"
                ).values("project_id")
            )
        elif self.request.user.is_authenticated and self.request.user.has_perm("projects.view_project"):
            project_filter = Q()
        else:
            project_filter = Q(is_public=True)
        return Project.objects.filter(project_filter).order_by("name")

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["projects"] = self.get_visible_projects()
        return context_data


class ProjectDistributionPackageIndex(PermissionRequiredMixin, TemplateView):
    """List all distribution packages for a project."""

    project: Project

    template_name = "simple_index/package_index.html"
    raise_exception = True
    permission_required = "projects.view_project"

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponseBase:
        self.project = get_object_or_404(Project, name=kwargs["project_name"])
        return super().dispatch(request, *args, **kwargs)

    def has_permission(self) -> bool:
        return self.project.is_public or self.request.user.has_perm(self.permission_required, self.project)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["packages"] = LegacyUpload.objects.order_by("-version", "content_filename").filter(
            name=self.kwargs["project_name"]
        )
        return context_data


class DownloadDistributionPackage(View):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponseBase:
        project = get_object_or_404(Project, name=kwargs["project_name"])
        distribution_package = get_object_or_404(LegacyUpload, content_filename=kwargs["path"])

        if not project.is_public and not self.request.user.has_perm("projects.view_project", project):
            raise Http404()

        # Respect the If-Modified-Since header.
        fullpath = Path(distribution_package.content.path)
        stat_obj = fullpath.stat()

        if not was_modified_since(request.META.get("HTTP_IF_MODIFIED_SINCE"), stat_obj.st_mtime):
            return HttpResponseNotModified()

        content_type, encoding = mimetypes.guess_type(str(fullpath))  # TODO: set mimetype on upload
        content_type = content_type or "application/octet-stream"
        response = FileResponse(fullpath.open("rb"), content_type=content_type)
        response.headers["Last-Modified"] = http_date(stat_obj.st_mtime)
        return response
