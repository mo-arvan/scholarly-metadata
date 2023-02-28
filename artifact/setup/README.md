# Setup

Instructions for creating or organizing the artifacts of a given project.

## Steps

- Copy the artifacts folder into your projects.
- Identify the first (or the main) procedure of running the scripts.
- (Optional) If the repository comes with specified requirements, use those.
- Select an appropriate docker image base
- Iteratively run the script that cover missing dependencies, fix bugs, etc.
- Finally, export the docker image to file using the command below `docker save` ()

### Docker Containers

```bash
source artifact/scripts/env.sh 

docker build -t ${PROJECT_NAME}_image -f artifact/setup/dockerfile artifact


docker build -t ${PROJECT_NAME}_ls_image -f artifact/setup/dockerfile_label_studio artifact



docker run --rm --gpus all -v ${PWD}:/workspace -it -p 8080:8080 ${PROJECT_NAME}_image bash
docker run --rm --gpus all -v ${PWD}:/workspace -it -p 8080:8080 -p 8081:8081 ${PROJECT_NAME}_image tmux
docker run --rm --gpus all -v ${PWD}:/workspace -v /mnt/2tb/clips:/clips  -it -p 8080:8080 -p 8081:8081 -p 9090:9090 ${PROJECT_NAME}_image tmux

docker run --rm --gpus all -v ${PWD}:/workspace -v /mnt/2tb/clips:/clips  -it --net stargaze-net --ip 172.18.0.101 ${PROJECT_NAME}_image tmux
# inside the container, run the required commands

```

#### Download Chats

```bash
docker build -t ${PROJECT_NAME}_dc_image -f artifact/setup/dockerfile_download_chats artifact

docker run --rm -v ${PWD}:/workspace ${PROJECT_NAME}_dc_image python src/download_chats.py
```


```bash
docker build -t ${PROJECT_NAME}_labeling_image -f artifact/setup/dockerfile_labeling artifact

docker run --rm -v ${PWD}:/workspace ${PROJECT_NAME}_dc_image python src/download_chats.py
```

### Useful tools

- `unzip`: `unzip file_name`
- `docker save --output hello-world.tar image_name`