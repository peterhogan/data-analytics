from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^demo/', include('demo.urls')),
    url(r'^admin/', admin.site.urls),
]
