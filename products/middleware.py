import ipaddress
from .models import AnalyticsEvent, StoreVisitSession

BOT_USER_AGENTS = (
    'bot', 'crawl', 'spider', 'slurp', 'facebookexternalhit',
    'whatsapp', 'curl', 'python-requests', 'lighthouse', 'pingdom'
)


def _extract_valid_ip(request):
    candidates = []
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        candidates.append(x_forwarded.split(',')[0].strip())
    if request.META.get('REMOTE_ADDR'):
        candidates.append(request.META.get('REMOTE_ADDR').strip())
    for cand in candidates:
        try:
            return str(ipaddress.ip_address(cand))
        except ValueError:
            continue
    return None


class AnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        purpose = (request.META.get('HTTP_PURPOSE') or request.META.get('HTTP_SEC_PURPOSE') or '').lower()
        if (
            request.method == 'GET'
            and 'prefetch' not in purpose
            and not path.startswith('/static/')
            and not path.startswith('/media/')
            and not path.startswith('/django-admin/')
            and not path.startswith('/mosabbiradmin/')
            and not path.startswith('/api/')
            and not path.startswith('/.well-known/')
            and path not in ('/favicon.ico', '/robots.txt', '/sitemap.xml')
        ):
            ua = request.META.get('HTTP_USER_AGENT', '')
            ua_lower = ua.lower()

            if ua and not any(b in ua_lower for b in BOT_USER_AGENTS):
                ip = _extract_valid_ip(request)

                if not request.session.session_key:
                    request.session.save()
                session_key = request.session.session_key

                if not request.session.get('visit_logged'):
                    request.session['visit_logged'] = True
                    try:
                        StoreVisitSession.objects.create(session_key=session_key, ip_address=ip)
                    except Exception:
                        pass

                device = 'Mobile' if any(w in ua_lower for w in ['mobile', 'android', 'iphone']) else 'Desktop'
                browser = (
                    'Chrome' if 'chrome' in ua_lower and 'edg' not in ua_lower
                    else ('Firefox' if 'firefox' in ua_lower else ('Safari' if 'safari' in ua_lower else 'Other'))
                )

                try:
                    AnalyticsEvent.objects.create(
                        ip_address=ip,
                        user_agent=ua[:200],
                        device_type=device,
                        browser=browser,
                        path=path[:250],
                        event_type='visit',
                        referrer=request.META.get('HTTP_REFERER', '')[:250],
                    )
                except Exception:
                    pass

        return self.get_response(request)
