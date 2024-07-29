from django.db import models

class ranking(models.Model):
    id = models.AutoField(primary_key=True)
    teamname = models.CharField(max_length=99,db_column='TeamName')
    points = models.IntegerField(db_column='Points')

    def __str__(self):
        return self.teamname

    class Meta:
        db_table = 'ranking'
        app_label = 'ranktable'

class games(models.Model):
    id = models.AutoField(primary_key=True)
    team1_name = models.CharField(max_length=99)
    team1_score = models.IntegerField()
    team2_name = models.CharField(max_length=99)
    team2_score = models.IntegerField()

    def __str__(self):
        return str(self.id)
    
    class Meta:
        db_table = 'games'
        app_label = 'ranktable'
