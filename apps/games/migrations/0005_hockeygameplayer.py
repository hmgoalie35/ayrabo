# Generated by Django 2.2.15 on 2020-08-17 01:21

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0007_auto_20181110_0412'),
        ('players', '0003_auto_20190421_2008'),
        ('games', '0004_auto_20200806_0224'),
    ]

    operations = [
        migrations.CreateModel(
            name='HockeyGamePlayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Updated')),
                ('is_starting', models.BooleanField(default=False, verbose_name='Is Starting')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='games.HockeyGame')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='players.HockeyPlayer')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='teams.Team')),
            ],
            options={
                'abstract': False,
                'unique_together': {('game', 'player')},
            },
        ),
    ]
