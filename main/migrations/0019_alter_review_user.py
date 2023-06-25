# Generated by Django 4.1.3 on 2023-06-14 09:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_education"),
        ("main", "0018_review_show"),
    ]

    operations = [
        migrations.AlterField(
            model_name="review",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to="accounts.userprofile"
            ),
        ),
    ]