import datetime
from django.utils.timezone import utc
from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions
from rest_framework import HTTP_HEADER_ENCODING
from django.utils.translation import gettext_lazy as _

def get_authorization_header(request):
    """
    Return request's 'Authorization:' header, as a bytestring.

    Hide some test client ickyness where the header can be unicode.
    """
    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if isinstance(auth, str):
        # Work around django test client oddness
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth


class ExpiringTokenAuthentication(TokenAuthentication):
    keyword = 'Token'
    model = None

    def get_model(self):
        if self.model is not None:
            return self.model
        from rest_framework.authtoken.models import Token
        return Token

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        if 'user_id' not in request.data or request.data['user_id'] == '':
            msg = _('User id filed id required or not null allowed.')
            raise exceptions.AuthenticationFailed(msg)
        try:
            user_id = int(request.data['user_id'])
        except ValueError:
            raise exceptions.AuthenticationFailed(_('Enter valid user id. it\'s integer filed.'))
        return self.authenticate_credentials(token, request.data['user_id'])

    def authenticate_credentials(self, key, user_id):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        if token.user.id != int(user_id):
            raise exceptions.AuthenticationFailed('Token does match with user token.')
        # utc_now = datetime.datetime.utcnow()
        #
        # if token.created < utc_now - datetime.timedelta(hours=24):
        #     raise exceptions.AuthenticationFailed('Token has expired')
        return (token.user, token)

