import openreview
import time
client = openreview.Client(baseurl='https://api.openreview.net',
                           username='<your username>', password='<your password>')
notes = openreview.tools.iterget_notes(
    client, invitation='ICLR.cc/2019/Conference/-/Blind_Submission')
for note in notes:
    print(note.content['title'])


def main():

    start_time =
