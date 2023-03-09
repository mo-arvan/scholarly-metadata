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
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

logger = logging.getLogger("PyPDF2")
logger.setLevel(logging.ERROR)


def main():

    results_df = pd.read_csv('results/keyword_match.csv', index_col=0)

    results_df["file_name"] = results_df["file_path"].apply(
        lambda x: x.split("/")[-1].split(".")[0].replace("-Paper", ""))

    neurips_papers = pd.read_csv('results/neurips_papers.csv')

    neurips_papers = neurips_papers.loc[~pd.isnull(
        neurips_papers["openreviewCode"])]

    neurips_papers["file_name"] = neurips_papers["url"].apply(
        lambda x: x.split("/")[-1].split(".")[0].replace("-Abstract", ""))

    avaiable_code = neurips_papers["file_name"].tolist()

    results_df["open_review_contains"] = results_df["file_name"].apply(
        lambda x: x in avaiable_code)

    # excluding a few failed text searches
    results_df = results_df.loc[~pd.isnull(results_df["contains"])]

    results_df["has_code"] = results_df["open_review_contains"] | results_df["contains"]

    results_df["year"] = results_df["file_path"].apply(
        lambda x: int(x.split("/")[1].split("_")[1]))

    results_df["conference"] = results_df["file_path"].apply(
        lambda x: x.split("/")[1].split("_")[0])

    conference_dict = {"interspeech": "Interspeech",
                       "neurips": "NeurIPS",
                       }

    results_df["conference"] = results_df["conference"].apply(
        lambda x: conference_dict[x])

    # left join with the results
    search_df = results_df[["conference", "year", "has_code"]].groupby(["conference", "year"]).agg(
        submissions_with_code=('has_code', 'sum'),
        total_submissions=('has_code', 'count')).reset_index()

    search_df["code_ratio"] = search_df["submissions_with_code"] / \
        search_df["total_submissions"]
    # interspeech_results["conference"] = "Interspeech"

    acl_results = pd.read_csv('results/acl.csv')

    all_results = pd.concat([search_df, acl_results])

    all_results["code_ratio"] = all_results["code_ratio"] * 100

    all_results = all_results.loc[all_results["year"] >= 2017]

    # plotting the results
    submissions_with_code_plot = sns.relplot(data=all_results,
                                             x="year",
                                             y="code_ratio",
                                             hue="conference",
                                             kind="line",
                                             style="conference",
                                             markers=True,
                                             facet_kws={'legend_out': True}) \
        .set(xlabel="Year", ylabel="% Artifact Submission", title="Artifact Submission Ratio")
    submissions_with_code_plot._legend.set_title('Conference')

    submissions_with_code_plot.savefig("results/artifact_inclusion.svg")
    submissions_with_code_plot.savefig("results/artifact_inclusion.png")

    total_submissions_plot = sns.relplot(data=all_results,
                                         x="year",
                                         y="total_submissions",
                                         hue="conference",
                                         kind="line",
                                         style="conference",
                                         markers=True,
                                         facet_kws={'legend_out': True}) \
        .set(xlabel="Year", ylabel="# Accepted Papers", title="Accepted Papers over Years")
    total_submissions_plot._legend.set_title('Conference')

    total_submissions_plot.savefig("results/total_submissions.svg")
    total_submissions_plot.savefig("results/total_submissions.png")

    # results_grouped.plot(x="year", y="count", kind="bar").get_figure().savefig(
    #     "results.png")
    # print(results_grouped.head())

    # submissions_with_code_plot = sns.relplot(data=agg_result,
    #                                          x="year",
    #                                          y="submissions_with_code",
    #                                          hue="conference",
    #                                          style="conference",
    #                                          markers=True,
    #                                          kind="line",
    #                                          facet_kws={'legend_out': True}) \
    #     .set(xlabel="Year", ylabel="# Published Papers with Code")
    # submissions_with_code_plot._legend.set_title('Conference')
    # ratio_list = []
    # for r in results_grouped["year"].unique():
    #     total = results_grouped.loc[results_grouped["year"]
    #                                 == r]["count"].sum()
    #     only_with_code = results_grouped.loc[np.logical_and(results_grouped["year"] == r,
    #                                                         results_grouped["contains"] == True)]["count"].sum()

    #     ratio_list.append((r, only_with_code * 100 / total))

    # ratio_df = pd.DataFrame(ratio_list, columns=["year", "ratio"])
    # sns.set()

    # results_grouped.plot(kind="bar", stacked=True, x="year", y="count", color="contains",
    #                      ).get_figure().savefig("results.png")

    # submission_with_code_ration_plot = sns.catplot(data=results_grouped,
    #                                                x="year",
    #                                                y="count",
    #                                                hue="contains",
    #                                                #    style="contains",
    #                                                #    markers=True,
    #                                                stacked=True,
    #                                                kind="bar",
    #                                                facet_kws={'legend_out': True}) \
    #     .set(xlabel="Year", ylabel="% Published Papers with Code")
    # # submission_with_code_ration_plot._legend.set_title('Conference')
    # submission_with_code_ration_plot.savefig("results" + ".png")
    # submission_with_code_ration_plot.savefig("results" + ".svg")
    # pdfFileObj = open('sample.pdf', 'rb')
    # pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    # pageObj = pdfReader.getPage(0)
    # print(pageObj.extractText())


if __name__ == '__main__':
    sns.set_theme()
    sns.set_style("darkgrid")
    main()
