import base64
import json
import re
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from django.conf import settings


class PaymentConfigurationError(Exception):
    pass


class PaymentGatewayError(Exception):
    pass


def normalize_mpesa_phone(phone_number):
    digits = re.sub(r'[^0-9]', '', phone_number or '')
    if digits.startswith('0') and len(digits) == 10:
        digits = f'254{digits[1:]}'
    elif digits.startswith('7') and len(digits) == 9:
        digits = f'254{digits}'
    if not re.fullmatch(r'254[17]\d{8}', digits):
        raise PaymentGatewayError(
            'Enter a valid Kenyan M-Pesa number, such as 0712345678.'
        )
    return digits


def _configuration():
    values = {
        'consumer key': settings.MPESA_CONSUMER_KEY,
        'consumer secret': settings.MPESA_CONSUMER_SECRET,
        'shortcode': settings.MPESA_SHORTCODE,
        'passkey': settings.MPESA_PASSKEY,
        'callback URL': settings.MPESA_CALLBACK_URL,
    }
    missing = [label for label, value in values.items() if not value]
    if missing:
        details = ', '.join(missing)
        raise PaymentConfigurationError(
            'M-Pesa checkout is not configured. Set Daraja ' + details + '.'
        )
    if settings.MPESA_ENVIRONMENT not in {'sandbox', 'production'}:
        raise PaymentConfigurationError(
            'MPESA_ENVIRONMENT must be "sandbox" or "production".'
        )
    return values


def _api_host():
    if settings.MPESA_ENVIRONMENT == 'production':
        return 'https://api.safaricom.co.ke'
    return 'https://sandbox.safaricom.co.ke'


def _post_json(url, payload, headers):
    request = Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={**headers, 'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode('utf-8'))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise PaymentGatewayError(
            'Could not contact M-Pesa. Please try again later.'
        ) from error


def start_mpesa_payment(phone_number, amount, account_reference, description):
    config = _configuration()
    credentials = (
        f"{config['consumer key']}:{config['consumer secret']}"
    ).encode('utf-8')
    authorization = base64.b64encode(credentials).decode('ascii')
    token_request = Request(
        f'{_api_host()}/oauth/v1/generate?grant_type=client_credentials',
        headers={'Authorization': f'Basic {authorization}'},
    )
    try:
        with urlopen(token_request, timeout=20) as response:
            token_payload = json.loads(response.read().decode('utf-8'))
            access_token = token_payload['access_token']
    except (
        HTTPError,
        URLError,
        TimeoutError,
        KeyError,
        json.JSONDecodeError,
    ) as error:
        raise PaymentGatewayError(
            'Could not authenticate with M-Pesa. Check the Daraja credentials.'
        ) from error

    timestamp = datetime.now(ZoneInfo('Africa/Nairobi')).strftime(
        '%Y%m%d%H%M%S'
    )
    password = base64.b64encode(
        f"{config['shortcode']}{config['passkey']}{timestamp}".encode('utf-8')
    ).decode('ascii')
    payload = {
        'BusinessShortCode': config['shortcode'],
        'Password': password,
        'Timestamp': timestamp,
        'TransactionType': 'CustomerPayBillOnline',
        'Amount': amount,
        'PartyA': phone_number,
        'PartyB': config['shortcode'],
        'PhoneNumber': phone_number,
        'CallBackURL': config['callback URL'],
        'AccountReference': account_reference[:12],
        'TransactionDesc': description[:13],
    }
    result = _post_json(
        f'{_api_host()}/mpesa/stkpush/v1/processrequest',
        payload,
        {'Authorization': f'Bearer {access_token}'},
    )
    if (
        result.get('ResponseCode') != '0'
        or not result.get('CheckoutRequestID')
    ):
        message = result.get('ResponseDescription')
        raise PaymentGatewayError(
            message or 'M-Pesa did not accept the payment request.'
        )
    return result
