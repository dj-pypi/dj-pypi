"""dj_pypi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from legacy_upload.views import LegacyUploadView
from simple_index.views import DownloadDistributionPackage, ProjectDistributionPackageIndex, ProjectIndex


urlpatterns = [
    path("admin/", admin.site.urls),
    path("upload/", LegacyUploadView.as_view(), name="legacy-upload"),
    path("simple/", ProjectIndex.as_view(), name="simple-project-index"),
    path(
        "simple/<slug:project_name>/",
        ProjectDistributionPackageIndex.as_view(),
        name="simple-project-distribution-package-index",
    ),
    path(
        "simple/<slug:project_name>/<path:path>",
        DownloadDistributionPackage.as_view(),
        name="download-distribution-package",
    ),
]
