import json,time
from bakalarka import sched


def setBlinds(vyska,uhol):
    print("Nastaví výšku: "+vyska+", uhol: "+uhol)


def initializer():
    aDate = time.strftime('%Y-%m-%d')
    with open("bakalarka/static/events.json", 'r') as f:
        data = json.loads(f.read()) 
        if aDate in data:
            for event in data[aDate]:
                
                datetime = aDate+" "+event['time']+":00"
                vyska = event['vyska']
                uhol = event['uhol']
                sched.add_job(setBlinds, 'date', run_date=datetime,args=[vyska, uhol])
    




initializer()
sched.add_job(initializer,'cron',hour ='0')

