from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name="home"),       # root → shows index.html
    path('admin/', admin.site.urls),
    path('shop/', include('shop.urls')),      # /shop/
    path('blog/', include('blog.urls')),      # /blog/
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
