from rest_framework.response import Response

class KattakonPermissionMixin:
    def check_kattakon(self, request):
        if not hasattr(request.user, 'kattakon'):
            return Response(
                {'error': 'faqqatgina "Kattakon" larga ruxsat bor jprqi!'},
                status=403
            )
        return None