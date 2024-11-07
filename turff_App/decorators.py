from django.shortcuts import redirect
from django.conf import settings

def custom_login_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return redirect(f'{settings.LOGIN_URL}?next={request.path}')
    return _wrapped_view
