# Generated by Django 4.1.3 on 2023-05-02 01:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0002_alter_education_hsc_cgpa_alter_education_hsc_year_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="education",
            name="bsc_cgpa",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="education",
            name="hsc_cgpa",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="education",
            name="ssc_cgpa",
            field=models.FloatField(blank=True, null=True),
        ),
    ]
