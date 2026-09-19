from functools import wraps

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login


def staff_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), login_url='dashboard:login')
        if not request.user.is_staff:
            messages.error(request, "You don't have permission to access the dashboard.")
            return redirect_to_login(request.get_full_path(), login_url='dashboard:login')
        return view_func(request, *args, **kwargs)
    return _wrapped
