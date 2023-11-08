import PyPDF2
import requests
import requests.utils
from bs4 import BeautifulSoup
import os
from tqdm import tqdm
import re
from multiprocessing import Pool
from functools import partial
import concurrent.futures
import pandas as pd
import logging
import time

from selenium import webdriver

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

logger = logging.getLogger("PyPDF2")
logger.setLevel(logging.ERROR)


def run_in_parallel_io_bound(func, iterable, max_workers=None, disable=False, **kwargs):
    """
    Run a function in parallel on a list of arguments
    :param disable: whether to disable the progress bar
    :param func: function to run
    :param iterable: list of arguments
    :param max_workers: maximum number of workers to use
    :param kwargs: keyword arguments to pass to the function
    :return: list of results
    """
    results = []
    number_of_entries = len(iterable)

    with tqdm(total=number_of_entries, disable=disable) as progress_bar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_dict = {
                executor.submit(func, item, **kwargs): index
                for index, item in enumerate(iterable)
            }
            for future in concurrent.futures.as_completed(future_dict):
                results.append(future.result())
                progress_bar.update(1)
    return results


def run_in_parallel_cpu_bound(func, iterable, max_workers=None, disable=False, total=None, **kwargs):
    """
    Run a function in parallel on a list of arguments
    :param disable: whether to disable the progress bar
    :param func: function to run
    :param iterable: list of arguments
    :param max_workers: maximum number of workers to use
    :param kwargs: keyword arguments to pass to the function
    :return: list of results
    """
    results = []
    if hasattr(iterable, "len"):
        total = len(iterable)

    with tqdm(total=total, disable=disable) as progress_bar:
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_dict = {
                executor.submit(func, item, **kwargs): index
                for index, item in enumerate(iterable)
            }
            for future in concurrent.futures.as_completed(future_dict):
                results.append(future.result())
                progress_bar.update(1)
    return results


def scrape_papers_info(papers_df):
    if isinstance(row_value, str):
        return row_value

    papers_dict_list = []
    for paper_info in papers_url_list:
        title, conference, year, url = paper_info

        proceedings_page = requests.get(f"https://papers.nips.cc{url}")

        if proceedings_page.status_code != 200:
            logger.warning(
                f"Failed to get proceedings page for {title} {conference} {year} {url}")
            continue

        parsed_html = BeautifulSoup(proceedings_page.text, 'html.parser')
        additional_info = parsed_html.find_all("a", class_="btn")

        paper_dict = {r.contents[0]: r.attrs['href']
                      for r in additional_info}

        open_review_url = next(
            filter(lambda x: "openreview" in x, paper_dict.values()), None)

        if open_review_url is not None:

            openreview_page = requests.get(open_review_url)

            if openreview_page.status_code == 200:

                openreview_response = BeautifulSoup(
                    openreview_page.text, 'html.parser')

                note_container = openreview_response.find_all(
                    "div", class_="note-content")

                assert len(note_container) == 1
                note_content = note_container[0].contents

                note_dict = {"openreview" + n.contents[0].text.replace(":", ""): get_openreview_field_value(
                    n) for n in note_content}

                paper_dict.update(note_dict)

        paper_dict['title'] = title
        paper_dict['conference'] = conference
        paper_dict['year'] = year
        paper_dict['url'] = url

        papers_dict_list.append(paper_dict)

        # pdf_url = parsed_html.find('a', text="PDF")['href']

    papers_df = pd.DataFrame(papers_dict_list)


def get_openreview_field_value(row):
    row_value = row.contents[-1].contents[0]
    if hasattr(row_value, "attrs") and "href" in row_value.attrs:
        return row_value.attrs["href"]
    else:
        return row_value.text


def get_neurips_info(paper_info):
    title, conference, year, url = paper_info

    paper_dict = {}
    paper_dict['title'] = title
    paper_dict['conference'] = conference
    paper_dict['year'] = year
    paper_dict['url'] = url

    proceedings_page = requests.get(url)

    if proceedings_page.status_code != 200:
        logger.warning(
            f"Failed to get proceedings page for {title} {conference} {year} {url}")
        return paper_dict

    parsed_html = BeautifulSoup(proceedings_page.text, 'html.parser')
    additional_info = parsed_html.find_all("a", class_="btn")

    for r in additional_info:
        if r.attrs['href'].startswith("/paper"):
            paper_dict[r.contents[0]
                       ] = f"https://papers.nips.cc{r.attrs['href']}"
        elif r.attrs['href'].startswith("http"):
            paper_dict[r.contents[0]] = r.attrs['href']

    open_review_url = next(
        filter(lambda x: isinstance(x, str) and "openreview" in x, paper_dict.values()), None)

    if open_review_url is not None:
        openreview_page = requests.get(open_review_url)
        if openreview_page.status_code == 200:
            openreview_response = BeautifulSoup(
                openreview_page.text, 'html.parser')

            note_container = openreview_response.find_all(
                "div", class_="note-content")

            assert len(note_container) == 1
            note_content = note_container[0].contents

            note_dict = {"openreview" + n.contents[0].text.replace(":", ""): get_openreview_field_value(
                n) for n in note_content}

            paper_dict.update(note_dict)

    return paper_dict


def get_neurips_papers(starting_year, ending_year):

    papers_url_list = []
    # options = webdriver.FirefoxOptions()
    # options.add_argument("--headless")

    def is_url_paper(url):
        return url.startswith("/paper")

    for year in range(starting_year, ending_year + 1):

        # driver = webdriver.Firefox(options=options)

        url = f"https://papers.nips.cc/paper/{year}"

        result = requests.get(url)
        if result.status_code != 200:
            # checking if the url is valid
            continue
        # driver.get(url)

        # parsed_html = BeautifulSoup(driver.page_source, 'html.parser')
        parsed_html = BeautifulSoup(result.text, 'html.parser')

        paper_elements = [x for x in parsed_html.find_all(
            'a') if is_url_paper(x.attrs['href'])]
        # title, confernece, year, url
        papers_url_list.extend(
            [(x.contents[0], "NeurIPS", year, f"https://papers.nips.cc{x.attrs['href']}") for x in paper_elements])

    # results = []
    # for paper_info in papers_url_list:
        # results.append(get_neurips_info(paper_info))

    results = run_in_parallel_io_bound(get_neurips_info, papers_url_list, 24)

    papers_df = pd.DataFrame(results)
    return papers_df


def get_interspeech_papers(starting_year, ending_year):
    """Get the papers from the interspeech conference.

    Args:
        starting_year (int): The year to start from.
        ending_year (int): The year to end at.

    Returns:
        list: A list of paper urls.
    """
    paper_info_list = []
    for year in range(starting_year, ending_year + 1):
        interspeech_year = f'interspeech_{year}'
        url = f'https://www.isca-speech.org/archive/{interspeech_year}/'
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')

        # find all elemnts with class 'paper'
        paper_urls_elements = [l for l in soup.find_all(
            'a', class_='w3-text') if l['href'].endswith('html')]

        paper_urls = [
            f"https://www.isca-speech.org/archive/pdfs/{interspeech_year}/{paper['href'].replace('html', 'pdf')}" for paper in paper_urls_elements]

        # get the href attribute of each element
        paper_list = [("INTERSPEECH", year, url) for url in paper_urls]

        paper_info_list.extend(paper_list)

    papers_df = pd.DataFrame(paper_info_list, columns=[
        "conference", "year", "url"])

    return papers_df


# def get_icml_papers(starting_year, ending_year):

#     papers_url_list = []
#     options = webdriver.FirefoxOptions()
#     options.add_argument("--headless")

#     def is_url_paper(url):
#         return url.startswith("/paper")

#     for year in range(starting_year, ending_year + 1):

#         driver = webdriver.Firefox(options=options)

#         url = f"https://icml.cc/virtual/{year}/papers.html"

#         result = requests.get(url)
#         if result.status_code != 200:
#             # checking if the url is valid
#             continue
#         driver.get(url)

#         # parsed_html = BeautifulSoup(driver.page_source, 'html.parser')
#         parsed_html = BeautifulSoup(result.text, 'html.parser')

#         paper_elements = [x for x in parsed_html.find_all(
#             'a') if is_url_paper(x.attrs['href'])]
#         # title, confernece, year, url
#         papers_url_list.extend(
#             [(x.contents[0], "NeurIPS", year, f"https://papers.nips.cc{x.attrs['href']}") for x in paper_elements])

#     papers_df = pd.DataFrame(papers_url_list, columns=[
#         "title", "conference", "year", "url"])
#     return papers_df


def main():

    start_time = time.perf_counter()


    neurips_papers = get_neurips_papers(2017, 2023)
    neurips_papers.to_csv("results/neurips_papers.csv", index=False)
    # icml_papers = get_icml_papers(2020, 2022)
    logger.info(f"Found {len(neurips_papers)} papers.")

    interspeech_papers = get_interspeech_papers(2017, 2023)
    interspeech_papers.to_csv("results/interspeech_papers.csv", index=False)

    logger.info(f"Found {len(interspeech_papers)} papers.")
    end_time = time.perf_counter()

    logger.info(f"Finished in {end_time - start_time} seconds")

    # return
    # download_interspeech_papers(interspeech_papers, download_dir)
    # search_papers(download_dir, 'github.com')



if __name__ == '__main__':
    main()


# def download_paper(url, headers, download_dir):
#     """
#     Download the paper from the interspeech conference.

#     Args:
#         url (str): The url of the paper.
#     """
#     interspeech_year_dir, file_name = url.split('/')
#     download_path = os.path.join(
#         download_dir, f'{interspeech_year_dir}/{file_name}')
#     if not os.path.exists(f'papers/{interspeech_year_dir}'):
#         os.makedirs(f'papers/{interspeech_year_dir}')

#     if os.path.exists(download_path):
#         return

#     paper_dl_url = f'https://www.isca-speech.org/archive/pdfs/{url}'

#     # download pdf file and save it in to a file
#     r = requests.get(paper_dl_url, headers=headers)

#     if r.status_code != 200:
#         logging.info(f"Failed to download {paper_dl_url}")
#         return
#     with open(download_path, 'wb') as f:
#         f.write(r.content)


# def download_interspeech_papers(url_list, download_dir):
#     """
#     Download the papers from the interspeech conference.

#     Args:
#         url_list (list): A list of paper urls.
#     """
#     headers = requests.utils.default_headers()

#     download_fn = partial(download_paper, headers=headers,
#                           download_dir=download_dir)

#     run_in_parallel_io_bound(download_fn, url_list,
#                              max_workers=16, disable=False)


# def search_pdf(paper_path, search_term):
#     """
#     Search the paper for a search term.

#     Args:
#         paper_path (str): The path of the paper.
#         search_term (str): The term to search for.
#     """
#     try:

#         pdfReader = PyPDF2.PdfReader(paper_path)
#         all_pages_text = "\n".join(
#             [page.extract_text() for page in pdfReader.pages])

#         all_pages_text = all_pages_text.replace('-\n', '')

#         r = re.search(r"\d\.\s*Reference", all_pages_text)
#         if r is not None:
#             references_start = r.start()
#         else:
#             references_start = len(all_pages_text)

#         text_excluding_references = all_pages_text[:references_start]
#         return paper_path, search_term in text_excluding_references
#     except Exception as e:
#         logger.info(f"Failed to search {paper_path} for {search_term}")
#         return paper_path, None


# def search_papers(papers_dir, search_term):
#     """
#     Search the papers for a search term.

#     Args:
#         papers_dir (str): The directory containing the papers.
#         search_term (str): The term to search for.
#     """
#     # get full path of all files in the papers directory including subdirectories
#     all_files = []
#     for root, dirs, files in os.walk(papers_dir):
#         for file in files:
#             if file.endswith('.pdf'):
#                 all_files.append(os.path.join(root, file))

#     search_fn = partial(search_pdf, search_term=search_term)

#     result = run_in_parallel_cpu_bound(search_fn, all_files,
#                                        max_workers=16, disable=False)

#     results_searched = [r for r in result if r]

#     results_with_code = [r[0] for r in results_searched if r[1]]

#     results_df = pd.DataFrame(result, columns=["file_path", "contains"])

#     results_df.to_csv('results/interspeech.csv')
#     logger.info(
#         f"Found {len(results_with_code)} papers with code. out of {len(results_searched)} papers.")
