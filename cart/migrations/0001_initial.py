# Generated by Django 4.2.6 on 2023-11-26 15:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('store', '0002_variation'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('userprofile', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cart_id', models.CharField(blank=True, max_length=250)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_price', models.FloatField()),
                ('payment_mode', models.CharField(max_length=150)),
                ('payment_id', models.CharField(max_length=250, null=True)),
                ('message', models.TextField(null=True)),
                ('tracking_no', models.CharField(max_length=150, null=True)),
                ('status', models.CharField(choices=[('Order confirmed', 'Order confirmed'), ('Shipped', 'Shipped'), ('Out for delivery', 'Out for delivery'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'), ('Return requested', 'Return requested'), ('Return processing', 'Return processing'), ('Returned', 'Returned')], default='Order confirmed', max_length=150)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userprofile.address')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField()),
                ('quantity', models.IntegerField()),
                ('status', models.CharField(choices=[('Order confirmed', 'Order confirmed'), ('Shipped', 'Shipped'), ('Out for delivery', 'Out for delivery'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'), ('Return requested', 'Return requested'), ('Return processing', 'Return processing'), ('Returned', 'Returned')], default='Order Confirmed', max_length=150)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cart.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product')),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.variation')),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cart.cart')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.variation')),
            ],
        ),
    ]
