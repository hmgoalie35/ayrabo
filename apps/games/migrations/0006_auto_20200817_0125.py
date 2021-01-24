# Generated by Django 2.2.15 on 2020-08-17 01:25

from django.db import migrations


def forwards_func(apps, schema_editor):
    # We don't support other sports at this time so we only have to do this for hockey
    HockeyGame = apps.get_model('games', 'HockeyGame')
    HockeyGamePlayer = apps.get_model('games', 'HockeyGamePlayer')
    qs = HockeyGame.objects.select_related(
        'home_team',
        'away_team'
    ).prefetch_related(
        'home_players_old',
        'away_players_old',
    )
    for game in qs.iterator():
        for home_player in game.home_players_old.all():
            HockeyGamePlayer.objects.create(
                game=game,
                team=game.home_team,
                player=home_player,
                is_starting=False
            )

        for away_player in game.away_players_old.all():
            HockeyGamePlayer.objects.create(
                game=game,
                team=game.away_team,
                player=away_player,
                is_starting=False
            )


def reverse_func(apps, schema_editor):
    # We don't support other sports at this time so we only have to do this for hockey
    HockeyGamePlayer = apps.get_model('games', 'HockeyGamePlayer')
    HockeyGamePlayer.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('games', '0005_hockeygameplayer'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_code=reverse_func)
    ]