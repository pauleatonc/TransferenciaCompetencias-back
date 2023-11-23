from rest_framework.routers import DefaultRouter

from applications.users.api.v1.usersViewSet import UserViewSet, GroupViewSet, PermissionViewSet

router = DefaultRouter()

router.register(r'users', UserViewSet, basename='users')
router.register(r'groups', GroupViewSet)
router.register(r'permissions', PermissionViewSet)

urlpatterns = router.urls