urlpatterns = [
    # path('admin/', admin.site.urls),
    path("tabletap/", include("tableapp.urls")),
    path("tabletap/admin/", admin.site.urls),
    path('tabletap/accounts/', include('allauth.urls')),

]
