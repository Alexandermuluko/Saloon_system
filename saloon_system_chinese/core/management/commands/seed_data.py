from datetime import date, time, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from core.models import Booking, Hairdresser, Service


class Command(BaseCommand):
    help = 'Populate sample data for services, hairdressers, users, and bookings.'

    def handle(self, *args, **options):
        services = [
            {
                'aliases': ['Haircut', 'Precision Haircut'],
                'name': 'Precision Haircut',
                'price': 500,
                'description': 'A convenient at-home haircut service for everyday refreshes and clean, polished results.',
                'image_url': 'https://images.unsplash.com/photo-1562322140-8baeececf3df?auto=format&fit=crop&w=1200&q=80',
            },
            {
                'aliases': ['Hair Styling', 'Style Design'],
                'name': 'Style Design',
                'price': 800,
                'description': 'A quick styling service for parties, dates, and polished everyday looks.',
                'image_url': 'https://images.unsplash.com/photo-1522336572468-97b06e8ef143?auto=format&fit=crop&w=1200&q=80',
            },
            {
                'aliases': ['Hair Treatment', 'Repair Treatment'],
                'name': 'Repair Treatment',
                'price': 1000,
                'description': 'A repair-focused treatment that restores softness and health to dry or damaged hair.',
                'image_url': 'https://images.unsplash.com/photo-1515377905703-c4788e51af15?auto=format&fit=crop&w=1200&q=80',
            },
            {
                'aliases': ['Braids Installation', 'Protective Braids'],
                'name': 'Protective Braids',
                'price': 1500,
                'description': 'A durable braiding service that looks neat and works well for at-home appointments.',
                'image_url': 'https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1?auto=format&fit=crop&w=1200&q=80',
            },
            {
                'aliases': ['Wash and Blow Dry', 'Wash and Style'],
                'name': 'Wash and Style',
                'price': 650,
                'description': 'Includes cleansing, basic treatment, and styling for fuller, natural-looking hair.',
                'image_url': 'https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?auto=format&fit=crop&w=1200&q=80',
            },
            {
                'aliases': ['Kids Haircut', 'Children Haircut'],
                'name': 'Children Haircut',
                'price': 400,
                'description': 'A relaxed children’s at-home haircut service that fits family schedules.',
                'image_url': 'https://images.unsplash.com/photo-1517832606299-7ae9b720a186?auto=format&fit=crop&w=1200&q=80',
            },
        ]

        hairdressers = [
            {
                'name': 'Jane Wanjiku',
                'specialization': 'Braiding specialist',
                'experience': '5 years',
                'bio': 'Specializes in knotless braids, twist styles, and neat protective looks.',
                'image_url': 'https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?auto=format&fit=crop&w=900&q=80',
                'is_verified': True,
            },
            {
                'name': 'Mary Achieng',
                'specialization': 'Styling specialist',
                'experience': '6 years',
                'bio': 'Specializes in event styling, soft waves, and polished everyday finishes.',
                'image_url': 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=900&q=80',
                'is_verified': True,
            },
            {
                'name': 'Faith Njeri',
                'specialization': 'Treatment specialist',
                'experience': '4 years',
                'bio': 'Focused on scalp care, repair treatment, and healthy hair maintenance.',
                'image_url': 'https://images.unsplash.com/photo-1491349174775-aaafddd81942?auto=format&fit=crop&w=900&q=80',
                'is_verified': True,
            },
            {
                'name': 'Lynn Atieno',
                'specialization': 'Wash and style specialist',
                'experience': '3 years',
                'bio': 'Skilled in gentle cleansing, everyday blow-drying, and comfortable home visits.',
                'image_url': 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=900&q=80',
                'is_verified': True,
            },
            {
                'name': 'Naomi Chebet',
                'specialization': 'Family haircut specialist',
                'experience': '5 years',
                'bio': 'Specializes in adult and children’s cuts for family appointments.',
                'image_url': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=900&q=80',
                'is_verified': True,
            },
            {
                'name': 'Zuri Kamau',
                'specialization': 'Advanced styling specialist',
                'experience': '7 years',
                'bio': 'Known for client-ready styling for events, shoots, and special occasions.',
                'image_url': 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=900&q=80',
                'is_verified': True,
            },
        ]

        created_services = 0
        service_map = {}
        for data in services:
            aliases = data.pop('aliases')
            service = Service.objects.filter(name__in=aliases).first()
            if service:
                created = False
                for key, value in data.items():
                    setattr(service, key, value)
                service.save()
            else:
                service = Service.objects.create(**data)
                created = True
            service_map[service.name] = service
            created_services += int(created)

        created_hairdressers = 0
        hairdresser_map = {}
        for data in hairdressers:
            hairdresser, created = Hairdresser.objects.update_or_create(name=data['name'], defaults=data)
            hairdresser_map[hairdresser.name] = hairdresser
            created_hairdressers += int(created)

        staff_user, staff_created = User.objects.get_or_create(
            username='staffdemo',
            defaults={
                'first_name': 'Store',
                'last_name': 'Admin',
                'email': 'staffdemo@salonhome.local',
                'is_staff': True,
            },
        )
        if staff_created:
            staff_user.set_password('demo12345')
            staff_user.save()

        customer_specs = [
            ('amanda', 'Amanda', 'Nganga', 'amanda@salonhome.local'),
            ('liwei', 'Li', 'Wei', 'liwei@salonhome.local'),
            ('nora', 'Nora', 'Kariuki', 'nora@salonhome.local'),
            ('chen', 'Chen', 'Yuan', 'chen@salonhome.local'),
        ]
        customers = []
        for username, first_name, last_name, email in customer_specs:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                },
            )
            if not created:
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.save()
            if created:
                user.set_password('demo12345')
                user.save()
            customers.append(user)

        today = date.today()
        booking_specs = [
            ('BK1001', customers[0], 'Amanda', '0701000001', 'Precision Haircut', 'Naomi Chebet', today + timedelta(days=1), time(9, 0), 'Westview Apartments', 'Needs a clean short cut before a work event.', 'Card', Booking.STATUS_ASSIGNED),
            ('BK1002', customers[1], 'Li Wei', '0701000002', 'Style Design', 'Mary Achieng', today + timedelta(days=1), time(11, 30), 'Riverside Residence', 'Soft curls for a dinner event.', 'Cash', Booking.STATUS_ON_THE_WAY),
            ('BK1003', customers[2], 'Nora', '0701000003', 'Repair Treatment', 'Faith Njeri', today, time(14, 0), 'Kilimani Gardens', 'Dry scalp and a need for a deeper repair treatment.', 'Cash', Booking.STATUS_IN_PROGRESS),
            ('BK1004', customers[3], 'Chen Yuan', '0701000004', 'Protective Braids', 'Jane Wanjiku', today + timedelta(days=2), time(10, 0), 'Syokimau Estate', 'Long hair braided neatly for a special occasion.', 'Card', Booking.STATUS_PENDING),
            ('BK1005', customers[0], 'Amanda', '0701000001', 'Wash and Style', 'Lynn Atieno', today + timedelta(days=3), time(16, 0), 'Westview Apartments', 'Simple wash, treatment, and smooth blow-dry.', 'Cash', Booking.STATUS_COMPLETED),
            ('BK1006', customers[1], 'Li Wei', '0701000002', 'Children Haircut', 'Naomi Chebet', today + timedelta(days=4), time(9, 30), 'Riverside Residence', 'A child’s haircut appointment for an 8-year-old.', 'Crypto', Booking.STATUS_ASSIGNED),
            ('BK1007', customers[2], 'Nora', '0701000003', 'Precision Haircut', 'Naomi Chebet', today - timedelta(days=1), time(15, 0), 'Kilimani Gardens', 'A practical trim before the weekend.', 'Cash', Booking.STATUS_COMPLETED),
            ('BK1008', customers[3], 'Chen Yuan', '0701000004', 'Style Design', 'Zuri Kamau', today + timedelta(days=5), time(13, 0), 'Syokimau Estate', 'A polished style before a shoot.', 'Card', Booking.STATUS_PENDING),
            ('BK1009', customers[0], 'Amanda', '0701000001', 'Repair Treatment', 'Faith Njeri', today + timedelta(days=6), time(12, 30), 'Westview Apartments', 'Post-color repair treatment for damaged ends.', 'Cash', Booking.STATUS_ARRIVED),
            ('BK1010', customers[1], 'Li Wei', '0701000002', 'Protective Braids', 'Jane Wanjiku', today + timedelta(days=7), time(8, 30), 'Riverside Residence', 'A long, boho-inspired braid style.', 'Card', Booking.STATUS_ASSIGNED),
            ('BK1011', customers[2], 'Nora', '0701000003', 'Wash and Style', 'Lynn Atieno', today + timedelta(days=2), time(17, 0), 'Kilimani Gardens', 'Quick wash and blow-dry before travel.', 'Cash', Booking.STATUS_PENDING),
            ('BK1012', customers[3], 'Chen Yuan', '0701000004', 'Children Haircut', 'Naomi Chebet', today + timedelta(days=3), time(10, 30), 'Syokimau Estate', 'Two children booking a joint haircut visit.', 'Cash', Booking.STATUS_ON_THE_WAY),
        ]

        created_bookings = 0
        for reference, customer, full_name, phone, service_name, hairdresser_name, appointment_date, appointment_time, location, notes, payment_method, status in booking_specs:
            booking = Booking.objects.filter(notes__startswith=f'{reference}').first()
            defaults = {
                'customer': customer,
                'full_name': full_name,
                'phone': phone,
                'service': service_map[service_name],
                'hairdresser': hairdresser_map[hairdresser_name],
                'appointment_date': appointment_date,
                'appointment_time': appointment_time,
                'location': location,
                'notes': f'{reference}: {notes}',
                'payment_method': payment_method,
                'status': status,
            }
            if booking:
                created = False
                for key, value in defaults.items():
                    setattr(booking, key, value)
                booking.save()
            else:
                Booking.objects.create(**defaults)
                created = True
            created_bookings += int(created)

        self.stdout.write(
            self.style.SUCCESS(
                f'Sample data setup complete: {created_services} services, {created_hairdressers} hairdressers, {created_bookings} bookings added.'
            )
        )
        self.stdout.write(
            f'Current counts -> services: {Service.objects.count()}, hairdressers: {Hairdresser.objects.count()}, bookings: {Booking.objects.count()}, users: {User.objects.count()}'
        )
        self.stdout.write('Staff demo login -> username: staffdemo | password: demo12345')
        self.stdout.write('Customer demo login -> usernames: amanda, liwei, nora, chen | password: demo12345')
