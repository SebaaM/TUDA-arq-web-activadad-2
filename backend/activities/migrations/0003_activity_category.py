from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("activities", "0002_participant_enrollment"),
    ]

    operations = [
        migrations.AddField(
            model_name="activity",
            name="category",
            field=models.CharField(default="General", max_length=80),
        ),
    ]
