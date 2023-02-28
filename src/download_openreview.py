import openreview
import time
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


client = openreview.Client(baseurl='https://api.openreview.net',
                           username='<your username>', password='<your password>')
notes = openreview.tools.iterget_notes(
    client, invitation='ICLR.cc/2019/Conference/-/Blind_Submission')
for note in notes:
    print(note.content['title'])


def main():

    start_time = time.perf_counter()

    end_time = time.perf_counter()

    logger.info(f"Total time: {end_time - start_time} seconds")
