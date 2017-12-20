from django.conf.urls import url, include
from rest_framework import routers
from . import views
from django.views.generic import TemplateView
from rest_framework.authtoken import views as authtoken_views
from push_notifications.api.rest_framework import APNSDeviceAuthorizedViewSet, GCMDeviceAuthorizedViewSet
from django.contrib import admin
from django.views.generic.base import RedirectView

admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'submissions', views.SubmissionViewSet, 'test')
router.register(r'device/apns', APNSDeviceAuthorizedViewSet)
router.register(r'device/gcm', GCMDeviceAuthorizedViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^api/register/', views.CreateUserView.as_view()),
    url(r'^api/', include(router.urls)),
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^$', views.index, name='index'),
#    url(r'^$', RedirectView.as_view(url='https://kinemai.com/', permanent=False), name='index'),
    url(r'^submit/(?P<sid>\w+)/$', views.analysis, name='analysis'),
    url(r'^submit/(?P<sid>\w+)/simulate/$', views.simulate, name='simulate'),
    url(r'^api/auth/token/', authtoken_views.obtain_auth_token),
    url(r'^admin/', include(admin.site.urls)),
#    url(r'^api-auth/token/', rest_framework.authtoken.views.obtain_auth_token),
]
