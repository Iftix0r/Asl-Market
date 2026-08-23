from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "AslFood Boshqaruv Paneli"
admin.site.site_title = "AslFood Admin"
admin.site.index_title = "Tizim Boshqaruvi"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
]
