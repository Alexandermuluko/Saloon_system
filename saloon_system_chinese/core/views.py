import json

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import (
    BookingAdminForm,
    BookingForm,
    HairdresserForm,
    LoginForm,
    RegisterForm,
    ServiceForm,
)
from .models import Booking, Hairdresser, PaymentAttempt, Service
from .payments import (
    PaymentConfigurationError,
    PaymentGatewayError,
    normalize_mpesa_phone,
    start_mpesa_payment,
)


def staff_required(view_func):
    return user_passes_test(lambda u: u.is_staff, login_url='login')(view_func)


class CustomLoginView(LoginView):
    template_name = 'admin-login.html'
    authentication_form = LoginForm

    def get_success_url(self):
        return reverse_lazy('post_login')


login_view = CustomLoginView.as_view()


def home(request):
    context = {
        'services': Service.objects.all(),
        'hairdressers': Hairdresser.objects.filter(is_verified=True),
    }
    return render(request, 'index.html', context)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('post_login')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Account created successfully.')
        return redirect('customer_booking_page')
    return render(request, 'register.html', {'form': form})


@login_required
def post_login_redirect(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    return redirect('customer_booking_page')


@login_required
def customer_booking_page(request):
    selected_service_id = request.GET.get('service')
    selected_service = None
    initial = None

    if selected_service_id:
        selected_service = Service.objects.filter(pk=selected_service_id).first()
        if selected_service:
            initial = {'service': selected_service.pk}

    form = BookingForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        booking = form.save(commit=False)
        booking.customer = request.user
        booking.status = Booking.STATUS_PENDING
        booking.save()
        messages.success(request, 'Booking submitted successfully.')
        return redirect('customer_booking_page')

    context = {
        'form': form,
        'services': Service.objects.all(),
        'hairdressers': Hairdresser.objects.filter(is_verified=True),
        'bookings': Booking.objects.filter(customer=request.user),
        'selected_service': selected_service,
    }
    return render(request, 'customer-service.html', context)


@login_required
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk, customer=request.user)
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Booking deleted successfully.')
    return redirect('customer_booking_page')


@login_required
def pay_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, customer=request.user)
    if request.method != 'POST':
        return redirect('customer_booking_page')
    if booking.payment_status == Booking.PAYMENT_PAID:
        messages.info(request, 'This booking has already been paid.')
        return redirect('customer_booking_page')

    try:
        phone_number = normalize_mpesa_phone(
            request.POST.get('phone_number', '')
        )
        amount = int(booking.service.price)
        if amount <= 0 or booking.service.price != amount:
            raise PaymentGatewayError(
                'M-Pesa requires a whole-number price greater than zero.'
            )
        response = start_mpesa_payment(
            phone_number=phone_number,
            amount=amount,
            account_reference=f'BOOKING-{booking.pk}',
            description=f'Salon booking {booking.pk}',
        )
        PaymentAttempt.objects.create(
            booking=booking,
            checkout_request_id=response['CheckoutRequestID'],
            merchant_request_id=response.get('MerchantRequestID', ''),
            phone_number=phone_number,
            amount=amount,
        )
        booking.payment_method = Booking.PAYMENT_MPESA
        booking.save(update_fields=['payment_method'])
        messages.success(
            request,
            f'Prompt sent to {phone_number}. Approve it and enter your PIN '
            'on your phone. The booking will show paid after confirmation.',
        )
    except (
        PaymentConfigurationError,
        PaymentGatewayError,
        ValueError,
    ) as error:
        messages.error(request, str(error))
    return redirect('customer_booking_page')


@csrf_exempt
@require_POST
def mpesa_callback(request):
    try:
        payload = json.loads(request.body)
        callback = payload['Body']['stkCallback']
        attempt = PaymentAttempt.objects.get(
            checkout_request_id=callback['CheckoutRequestID']
        )
    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
        KeyError,
        TypeError,
        PaymentAttempt.DoesNotExist,
    ):
        return JsonResponse(
            {'ResultCode': 1, 'ResultDesc': 'Payment request not found'},
            status=400,
        )

    attempt.result_description = callback.get('ResultDesc', '')[:255]
    if callback.get('ResultCode') == 0:
        items = callback.get('CallbackMetadata', {}).get('Item', [])
        metadata = {
            item.get('Name'): item.get('Value')
            for item in items
            if isinstance(item, dict)
        }
        receipt_number = metadata.get('MpesaReceiptNumber', '')
        amount = metadata.get('Amount')
        try:
            confirmed_amount = int(amount)
        except (TypeError, ValueError):
            confirmed_amount = None
        if confirmed_amount != attempt.amount or not receipt_number:
            attempt.status = PaymentAttempt.STATUS_FAILED
            attempt.result_description = (
                'Payment confirmation details did not match the request.'
            )
        else:
            attempt.status = PaymentAttempt.STATUS_PAID
            attempt.receipt_number = str(receipt_number)[:30]
            Booking.objects.filter(pk=attempt.booking_id).update(
                payment_status=Booking.PAYMENT_PAID
            )
    else:
        attempt.status = PaymentAttempt.STATUS_FAILED
    attempt.save(
        update_fields=['status', 'receipt_number', 'result_description']
    )
    return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})


@staff_required
def admin_dashboard(request):
    services = Service.objects.all()
    hairdressers = Hairdresser.objects.all()
    bookings = Booking.objects.select_related('service', 'hairdresser', 'customer')
    context = {
        'services': services,
        'hairdressers': hairdressers,
        'bookings': bookings,
        'service_count': services.count(),
        'hairdresser_count': hairdressers.count(),
        'booking_count': bookings.count(),
        'pending_count': bookings.filter(status=Booking.STATUS_PENDING).count(),
    }
    return render(request, 'admin-dashboard.html', context)


@staff_required
def service_create(request):
    return handle_crud_form(
        request=request,
        form_class=ServiceForm,
        template_title='Add service',
        submit_label='Save service',
        success_message='Service saved successfully.',
    )


@staff_required
def service_update(request, pk):
    service = get_object_or_404(Service, pk=pk)
    return handle_crud_form(
        request=request,
        form_class=ServiceForm,
        instance=service,
        template_title='Edit service',
        submit_label='Update service',
        success_message='Service updated successfully.',
    )


@staff_required
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Service deleted successfully.')
    return redirect('admin_dashboard')


@staff_required
def hairdresser_create(request):
    return handle_crud_form(
        request=request,
        form_class=HairdresserForm,
        template_title='Add hairdresser',
        submit_label='Save hairdresser',
        success_message='Hairdresser information saved successfully.',
    )


@staff_required
def hairdresser_update(request, pk):
    hairdresser = get_object_or_404(Hairdresser, pk=pk)
    return handle_crud_form(
        request=request,
        form_class=HairdresserForm,
        instance=hairdresser,
        template_title='Edit hairdresser',
        submit_label='Update hairdresser',
        success_message='Hairdresser information updated successfully.',
    )


@staff_required
def hairdresser_delete(request, pk):
    hairdresser = get_object_or_404(Hairdresser, pk=pk)
    if request.method == 'POST':
        hairdresser.delete()
        messages.success(request, 'Hairdresser deleted successfully.')
    return redirect('admin_dashboard')


@staff_required
def booking_update(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    return handle_crud_form(
        request=request,
        form_class=BookingAdminForm,
        instance=booking,
        template_title='Edit booking',
        submit_label='Update booking',
        success_message='Booking updated successfully.',
    )


@staff_required
def booking_admin_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Booking deleted successfully.')
    return redirect('admin_dashboard')


def handle_crud_form(request, form_class, template_title, submit_label, success_message, instance=None):
    form = form_class(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, success_message)
        return redirect('admin_dashboard')
    return render(
        request,
        'admin-form.html',
        {
            'form': form,
            'page_title': template_title,
            'submit_label': submit_label,
            'is_edit': instance is not None,
        },
    )
