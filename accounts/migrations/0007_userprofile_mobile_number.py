# Generated by Django 4.1.3 on 2023-06-25 03:50

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ("taggit", "0005_auto_20220424_2025"),
        ("accounts", "0006_education"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="mobile_number",
            field=taggit.managers.TaggableManager(
                help_text="A comma-separated list of tags.",
                through="taggit.TaggedItem",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        ),
    ]