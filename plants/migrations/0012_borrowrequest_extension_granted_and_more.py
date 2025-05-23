# Generated by Django 4.2.19 on 2025-04-29 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plants', '0011_borrowrequest_extension_requested_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='borrowrequest',
            name='extension_granted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='borrowrequest',
            name='status',
            field=models.CharField(choices=[('Pending', 'pending'), ('Approved', 'approved'), ('Rejected', 'rejected')], default='Pending', max_length=10),
        ),
    ]
