from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from ranktable.models import *
from ranktable.forms import *
import pandas

def index(request):
    gameslist = games.objects.all()
    data = ranking.objects.all().order_by('-points','teamname')
    if gameslist.count() < 1 and data.count() > 0:
        data.delete()
    # to order alphabetically, the space is removed first (only works on second reload)
    for d in data:
        d.teamname = d.teamname.strip()
        d.save()
    if request.method == 'GET':
        form = formfields()
    elif request.method == 'POST':
        form = formfields(request.POST,request.FILES)
        if request.FILES != {}:
            emptypreviousranking = ranking.objects.all().delete()
            emptypreviousgames = games.objects.all().delete()

            df = pandas.read_csv(request.FILES['csvfile'],names=['team_1_name', 'team_1_score', 'team_2_name', 'team_2_score'])

            for index, row in df.iterrows():
                gameinput(row['team_1_name'],row['team_1_score'],row['team_2_name'],row['team_2_score'])

                if row['team_1_score'] == row['team_2_score']:
                    teamupdate(row['team_1_name'],1)
                    teamupdate(row['team_2_name'],1)
                elif row['team_1_score'] > row['team_2_score']:
                    teamupdate(row['team_1_name'],3)
                    teamupdate(row['team_2_name'],0)
                elif row['team_1_score'] < row['team_2_score']:
                    teamupdate(row['team_1_name'],0)
                    teamupdate(row['team_2_name'],3)

            return redirect(request.META['HTTP_REFERER'])
    return render(request,'ranktable/index.html',{'form':form,'data':data,'games':gameslist})

def modifygame(request,gameid):
    gamedata = games.objects.filter(id=gameid)

    # found, edit game details
    if gamedata.count() > 0:
        origamedata = games.objects.get(id=gameid)
        if request.method == 'POST':
            form = gameform(request.POST)
            if form.is_valid():

                # undo ranking of previous data, reduce previous points
                team1 = ranking.objects.get(teamname=origamedata.team1_name.strip())
                team2 = ranking.objects.get(teamname=origamedata.team2_name.strip())
                if origamedata.team1_score > origamedata.team2_score:
                    team1.points -= 3
                    print("reducing team1")
                elif origamedata.team1_score < origamedata.team2_score:
                    team2.points -= 3
                    print("reducing team2")
                elif origamedata.team1_score == origamedata.team2_score:
                    team1.points -= 1
                    team2.points -= 1
                    print("reducing draw")
                team1.save()
                team2.save()

                getdata1 = ranking.objects.get(teamname=origamedata.team1_name.strip())
                getdata2 = ranking.objects.get(teamname=origamedata.team2_name.strip())
                print("first",getdata1.teamname,getdata1.points,getdata2.teamname,getdata2.points,origamedata.team1_score,origamedata.team2_score)

                # calculate and add points based on latest modified data
                team1 = ranking.objects.get(teamname=form.cleaned_data['team1_name'])
                team2 = ranking.objects.get(teamname=form.cleaned_data['team2_name'])
                if form.cleaned_data['team1_score'] > form.cleaned_data['team2_score']:
                    team1.points += 3
                    print("adding point1")
                elif form.cleaned_data['team1_score'] < form.cleaned_data['team2_score']:
                    team2.points += 3
                    print("adding point2")
                elif form.cleaned_data['team1_score'] == form.cleaned_data['team2_score']:
                    team1.points += 1
                    team2.points += 1
                    print("adding draw")
                team1.save()
                team2.save()

                getdata1 = ranking.objects.get(teamname=origamedata.team1_name.strip())
                getdata2 = ranking.objects.get(teamname=origamedata.team2_name.strip())
                print(getdata1.teamname,getdata1.points,getdata2.teamname,getdata2.points,form.cleaned_data['team1_score'],form.cleaned_data['team2_score'])

                origamedata.team1_name = form.cleaned_data['team1_name']
                origamedata.team1_score = form.cleaned_data['team1_score']
                origamedata.team2_name = form.cleaned_data['team2_name']
                origamedata.team2_score = form.cleaned_data['team2_score']
                origamedata.save()

                return redirect(reverse('index'))
        elif request.method == 'GET':
            form = gameform(instance=origamedata)

    # not found, create new game
    else:
        if request.method == 'POST':
            form = gameform(request.POST)
            if form.is_valid():
                #check if team ranking does not exist then create new
                teamupdate(form.cleaned_data['team1_name'],0)
                teamupdate(form.cleaned_data['team2_name'],0)

                # create new game input
                gameinput(form.cleaned_data['team1_name'],form.cleaned_data['team1_score'],
                          form.cleaned_data['team2_name'],form.cleaned_data['team2_score'])
                
                # calculate points based on new data
                team1 = ranking.objects.get(teamname=form.cleaned_data['team1_name'])
                team2 = ranking.objects.get(teamname=form.cleaned_data['team2_name'])
                if form.cleaned_data['team1_score'] > form.cleaned_data['team2_score']:
                    team1.points += 3
                elif form.cleaned_data['team1_score'] < form.cleaned_data['team2_score']:
                    team2.points += 3
                elif form.cleaned_data['team1_score'] == form.cleaned_data['team2_score']:
                    team1.points += 1
                    team2.points += 1
                team1.save()
                team2.save()

                return redirect(reverse('index'))
        elif request.method == 'GET':
            form = gameform()

    return render(request,'ranktable\gameform.html',{'form':form})

def deletegame(request,gameid):
    gamedata = games.objects.get(id=gameid)
    team1 = ranking.objects.get(teamname=gamedata.team1_name.strip())
    team2 = ranking.objects.get(teamname=gamedata.team2_name.strip())
    if gamedata.team1_score > gamedata.team2_score:
        team1.points -= 3
    elif gamedata.team1_score < gamedata.team2_score:
        team2.points -= 3
    elif gamedata.team1_score == gamedata.team2_score:
        team1.points -= 1
        team2.points -= 1
    team1.save()
    team2.save()
    gamedata.delete()
    return HttpResponseRedirect(reverse('index'))


# Custom functions

def teamupdate(name,pointsvalue):
    team = ranking.objects.filter(teamname=name)
    if team.count() > 0:
        for t in team:
            t.points += pointsvalue
            t.save()
    else:
        new = ranking(teamname=name,points=pointsvalue)
        new.save()

def gameinput(name1,score1,name2,score2):
    new = games(team1_name=name1,team1_score=score1,team2_name=name2,team2_score=score2)
    new.save()