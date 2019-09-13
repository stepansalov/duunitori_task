from django.shortcuts import render
from django.http import HttpResponse
from .models import Greeting
import csv
import requests
from datetime import datetime

CSV_URL = 'https://skyhood-duunitori5.s3.eu-central-1.amazonaws.com/rekry/jobentry_export_2019-8-23T9_59.csv'
COUNT_SECONDS_PER_DAY = 86400

# Create your views here.
def index(request):

    with requests.Session() as s:
        download = s.get(CSV_URL)
        decoded_content = download.content.decode('utf-8')
        job_entry = csv.reader(decoded_content.splitlines(), delimiter=';')
        fields = job_entry.__next__()
        if not fields.count("pageviews_all") or\
           not fields.count("applyclicks_all") or\
           not fields.count("date_posted") or\
           not fields.count("date_ends"):
            my_text = "No required fields in csv file"
            return render(request, "index.html", locals())
        else:
            index_pw = fields.index("pageviews_all")
            index_ac = fields.index("applyclicks_all")
            index_start = fields.index("date_posted")
            index_finish = fields.index("date_ends")

        page_view = []
        page_view_drow = []
        apply_click_drow = []
        count = 0
        for v in job_entry:
            dt_start = datetime.strptime(v[index_start], "%d.%m.%Y")
            dt_finish = datetime.strptime(v[index_finish], "%d.%m.%Y")
            dt = dt_finish - dt_start
            visible = dt.total_seconds() / COUNT_SECONDS_PER_DAY
            page_view.append(int(v[index_pw]))
            count += int(v[index_pw])
            page_view_drow.append(int(v[index_pw]) / visible)
            apply_click_drow.append(int(v[index_ac]) / visible)

        average = count / len(page_view)
        page_view.sort()
        if (len(page_view) % 2):
            index = int((len(page_view) + 1) / 2)
            median = page_view[index]
        else:
            index = int(len(page_view) / 2)
            median = (page_view[index] + page_view[index + 1]) / 2
        my_text = "Average: {}, Median: {}".format(average, median)

    return render(request, "index.html", locals())


def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, "db.html", {"greetings": greetings})
