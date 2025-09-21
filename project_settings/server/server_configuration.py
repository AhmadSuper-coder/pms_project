
def get_installed_app():
    return [list(app.values())[0] for app in INSTALLED_APPS_SERVER]

INSTALLED_APPS_SERVER = [
    {0: 'django.contrib.admin'},
    {1: 'django.contrib.auth'},
    {2: 'django.contrib.contenttypes'},
    {3: 'django.contrib.sessions'},
    {4: 'django.contrib.messages'},
    {5: 'django.contrib.staticfiles'},
    {6: 'django_extensions'},
    {7: 'rest_framework'},
    {8: 'rest_framework_simplejwt'},
    {9: 'account'},
    {10: "corsheaders"},
    {11: 'backend_apps.userprofile'},
    {12: 'backend_apps.payment'},
    {13: 'cloudinary'},
    {14: 'cloudinary_storage'},
]
