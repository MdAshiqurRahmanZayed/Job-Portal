# Generated by Django 4.1.3 on 2023-06-14 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0016_review"),
    ]

    operations = [
        migrations.AlterField(
            model_name="review",
            name="description",
            field=models.CharField(max_length=200),
        ),
    ]
