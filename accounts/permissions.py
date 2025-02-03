from rest_framework import permissions, exceptions

from django.core.cache import cache

#Modelo de permisos
class ModelsPermission(permissions.BasePermission):
	perms_map = {
		'GET': ['%(app_label)s.view_%(model_name)s'],
		'OPTIONS': [],
		'HEAD': [],
		'POST': ['%(app_label)s.add_%(model_name)s'],
		'PUT': ['%(app_label)s.update_%(model_name)s'],
		'PATCH': ['%(app_label)s.update_%(model_name)s'],
		'DELETE': ['%(app_label)s.delete_%(model_name)s'],
	}
	authenticated_users_only = True

	def get_required_permissions(self, method, model_attrs, user):
		kwargs = {
			'app_label': model_attrs['app_label'],
			'model_name': model_attrs['model_name']
		}

		if method not in self.perms_map:
			raise exceptions.MethodNotAllowed(method)

		kwargs['perms'] = [perm % kwargs for perm in self.perms_map[method]]

		return kwargs

	def has_permission(self, request, view):
		return True
		if not request.user.is_superuser:
			model_attrs = {}
			if hasattr(view, 'queryset') or hasattr(view, 'get_queryset'):
				queryset = self._queryset(view)
				model_attrs['app_label'] = queryset.model._meta.app_label
				model_attrs['model_name'] = queryset.model._meta.model_name
			else:
				model_attrs = view.model_attrs
			perms = self.get_required_permissions(request.method, model_attrs, request.user)

		return True if request.user.is_superuser else self.check_perms(request.user, perms)

	def check_perms(self, user, perms):
		
		action_perm = False

		if cache.get('actions_%s' % user.pk) and perms['model_name'] in cache.get('actions_%s' % user.pk):
			permissions = cache.get('actions_%s' % user.pk)[perms['model_name']]
			action = perms['perms'][0][perms['perms'][0].find(".")+1:].split("_")[0]
			action_perm = True if { 'menu_permission__action': f"{action}_{perms['model_name']}" } in permissions else False
		return action_perm

	def _queryset(self, view):
		assert hasattr(view, 'get_queryset') or getattr(view, 'queryset', None) is not None, (
			'Cannot apply {} on a view that does not set '
			'`.queryset` or have a `.get_queryset()` method.'
		).format(self.__class__.__name__)

		if hasattr(view, 'get_queryset'):
			queryset = view.get_queryset()
			assert queryset is not None, (
				'{}.get_queryset() returned None'.format(view.__class__.__name__)
			)
			return queryset
		return view.queryset
