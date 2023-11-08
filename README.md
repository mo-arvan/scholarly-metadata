# Reproducibility Analysis

This repository contains the code for analyzing publications in [NeurIPS Proceedings](https://papers.nips.cc/), (ACL Anthology)[https://aclanthology.org/]), and (ISCA Archive)[https://www.isca-speech.org].


## Steps 

Build the docker image:

```bash

docker build -t reproducibility-analysis -f artifact/setup/dockerfile artifact

```

Run the docker image:

```bash
docker run -it --rm -v $(pwd):/workspace reproducibility-analysis bash
```

First, download the metadata for NeurIPS and Interspeech:

```bash
python src/find_papers.py 
```

Then download the papers:

```bash
python src/download_papers.py
```
