from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("", include("core.urls")),
    path("investments/", include("investments.urls")),
    path("loans/", include("loans.urls")),
    path("trading/", include("trading.urls")),
    path("deposit/", include("deposits.urls")),
    path("withdraw/", include("accounts.withdrawal_urls")),
    path("", include("accounts.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)