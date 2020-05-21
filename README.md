# Flask-Redis-Docker Template

This project ties together [Flask](http://flask.pocoo.org), [Redis](http://redis.io), [RQ (Redis Queue)](http://python-rq.org) and [Docker](http://docker.com) in a simple demo application. It can serve as template for other projects as well as an introduction on how to use Flask with RQ while managing it all with [docker-compose](http://docs.docker.com/compose).

In the web application you can launch long running jobs which are put into a RQ task queue. From there a RQ worker picks it up and executes it. During execution the job reports back some progress information and  – if execution was successful – the job result.

## Screenshot
![screenshot](figure/demo.png)


## Quickstart

Clone the repository, cd into it and run
```bash
sudo docker-compose build
sudo docker-compose up -d
```

point your browser to http://localhost:5000. There is also rq-dashboard running on http://localhost:5555

## Docker containers

For each component of this project a separate docker container is afforded, controlled ("orchestrated") by docker-compose.

For the sake of simplicity, the same image is used for the separate containers. The image stems from [python:3.6-stretch](https://hub.docker.com/_/python), which contains a debian 9 linux. Instead of debian a more lightweight image like alpine could also be used.

The are four containers in this project at work.
* server: where are Flask web application runs
* worker: where the RQ worker process runs
* dashboard: where the rq-dashboard monitoring web application runs
* redis: containing the redis server

The image is build from `project/Dockerfile`. This one Dockerfile includes all the necessary python components and their dependencies from `project/requirements.txt`. Because we're using the same image for multiple purposes like the flask application, the rqworker and the rq-dashboard it has to contain all of these components. In an advanced use case you want to build different images which are tailored to their individual purposes.

For the redis server container the out-of-the-box [redis](https://hub.docker.com/_/redis) image is used - not much use building a image for redis by ourself.

## docker-compose in development and production

To give an example of a development workflow with docker-compose two configuration files are used. A feature of docker-compose is to have multiple configuration files layered on top of each other where later files override settings from previous ones.

In this project the default `docker-compose.yml` runs the application in aproduction while the additional `docker-compose-development.yml` runs the application in a way more suitable for development.

To run the application in a production like manner:
```
sudo docker-compose up -d
```
This will start the docker containers defined in docker-compose.yml. It is equivalent to running `docker-compose -f docker-compose.yml up -d`

To start the application in a development manner:
```
docker-compose -f docker-compose.yml -f docker-compose-development.yml up -d
```
This will read the configuration from docker-compose.yml and include the changes stated in docker-compose-development.yml before running the containers. By this way we alter the configuration given in the first file by the configuration from the second.

## docker-compose.yml

docker-compose.yml defines a service made up of four containers. A service is a group of containers and additional settings that make up an docker-compose application.
```yaml
services:
  server:
    build: ./project
    image: master-image
    ports:
      - 5000:5000
    command: gunicorn --workers 4 --bind 0.0.0.0:5000 --timeout 120 'server:create_app()'
    …
  worker:
    image: master-image
    depends_on:
      - redis
    command: rq worker --name worker --url redis://redis:6379/0
    …
  dashboard:
    image: master-image
    ports:
      - 5555:5555
    depends_on:
      - redis
    command: rq-dashboard --port 5555 --redis-url redis://redis:6379/0
    …
  redis:
    image: redis
```

### Reuse of images
In order to use the same image on multiple containers we have one container build it, name it, store it, and then reuse it on the other containers. `build: ./project` tells docker-compose to build an image from the Dockerfile it finds under the ./app directory. The subsequent `image: master-image` tells it to store that image under the name *master-image*. The `image: master-image` lines on the other containers refer to that image by its name. The choice of building the image in the context of the *web* container is arbitrary, you could to this on anyone of the other containers.

Instead of reusing the same image we could have said `build: ./project` on all of the three containers and leave out the `image: master-image` lines. This would result in three individual but identical images being build.

However, we do specify a different *command:* on each container. As we set up the image in the Dockerfile to be universaly usable, no specific command is run from there. Which means that if you would run the image outside of docker-compose on its own it would do nothing and just exit.

#### web container
On the *web* container `command: gunicorn --workers 4 --bind 0.0.0.0:5000 --timeout 120 'server:create_app()'` tells docker-compose to run (in the container) the gunicorn web server. *-b :5000* tells gunicorn to bind to (listen to) port 5000 on whatever IPs the container has. *'server:create_app()'* points gunicorn to the place where the flask app factory is. It in effect tells gunicorn to look for the python module *server* in its working directory (which we set to */app* in the Dockerfile) and look for the app egnerating function *create_app* which must create a valid flask application instance. Gunicorn with its dependencies and all the files that make up our web application have been copied into the image during the Dockerfile build process.

#### worker container
On the *worker* container `command: rqworker --name worker --url redis://redis:6379/0` tells docker-compose to run a *rqworker* process. *--url redis://redis:6379/0* tells the worker where it finds the redis server from where it fetches the jobs to execute and sends back the results. As the same image is used, the working directory of the worker is also /app, which again contains a copy of the web application files placed into the image. The rqworker needs access to the *jobs.py* file where it find the code to excecute jobs. After all rqworker is a python program that needs to have the python modules in reach which it is supposed to execute.

#### dashboard container
On the *dashboard* container `command: rq-dashboard --port 5555 --redis-url redis://redis:6379/0` tells docker to run the rq-dashboard application. The application gets told were to open the web server port and where to find the redis server it should monitor. In the same way as with the web and worker container the working directory of the rq-dashboard app is set to /app where a copy of the web application files resides. But in this case it does not actually matter, rq-dashboard does not need access to flask or tasks.py files and would run just as fine in a different working directory.

#### redis container
For the *redis* container we specify that we want to use a prebuild image from [Docker Hub](https://hub.docker.com/_/redis) rather than a self made one, for which a simple `image: redis` is sufficient.  The default configuration of redis pretty much suits us, so we don't need to set any options.

### Networking
docker-compose automatically sets up local network for our service where the containers can talk to each other; usually in the 172.x.x.x range. It also ensures that containers can address each other by their names. That's why we can write redis://redis:6379 without knowing the actual IP of the redis container.

## docker-compose-development.yml

docker-compose-development.yml is the overlay configuration file with works in conjunction with docker-compose.yml, so it only states the changes to it.
```yaml
services:
  server:
    container_name: server
    environment:
      - FLASK_APP=server:create_app()
      - FLASK_DEBUG=1
    volumes:
      - ./project:/app
    command: flask run --host=0.0.0.0

  worker:
     container_name: worker
     volumes:
      - ./project:/app
  …
```

One thing it does is to override *command:* on the web container to use a different web server. Instead of gunicorn in  docker-compose.yml it uses the web server bundled with flask:
```yaml
    command: flask run --host=0.0.0.0:
```
For the flask web server to work we also need to set some environment variables:
```
    environment:
      - FLASK_APP=server:create_app()
      - FLASK_DEBUG=1
```
This tells flask where to find the application instance and activates debug mode.

Using the bundled flask web server is not recommended for production use, but has some advantages during development. It comes with a build in debugger and it will automatically reload when you make changes to the source files – a feature we utilize in our workflow.

### Container names
We also set *container_name:* when in development. This allows for easy reference to a container in docker commands executed from the shell. In the docker command line arguments containers can either be referenced by their *container id* or by their *container name*. Both of them have to be unique over all docker containers on a host and that's not just the ones from our project. Even though we specified web:, worker:, dashboard: and redis: in docker-compose.yml this will only be local to our service and for e.g. network name resolution, but they are not the final container names. Without the *container_name:* option docker-compose will auto generate a name for every container and make sure it's unique.

For example
```
  server:
    container_name: server
```
assigns the name 'server' to the server container. Now we can e.g. inspect the logs by `docker-compose logs server` rather than `docker-compose logs myproject_server_1` or whatever name the container got auto assigned.

Explicitly naming containers however is not a good thing for production, as you might happen to have more than one called 'server' or 'redis' on the same host.

### Automatic reload on source file changes
The bundled flask development web server has the ability to auto reload itself when it detects a change to a source file. This comes in handy during development because you don't have manually restart the server to see the effect of the changes you've made. But as we are running the web server inside a container changes to files on the host file system e.g. in the *app/* directory must affect files in the container. This is done by mounting the the *./project* directory on the host to the */app* in the container.
```
  volumes:
    - ./project:/app
```
Note that you can mount to a directory inside a container even when that directory is not empty. The mounted directory will  shadow the contents of the target directory. In our case the /app directory already contains files that have been copied during the image build, but these files will be shadowed by the mounted directory (./project).

Auto reload does not only work for the flask web server inside the web container. The rqworker will also use the latest version of a source files when it starts to execute a job. Because it will reload itself everytime it executes a job anyway (see the section about worker performance in the RQ documentation for details).

## Working with containers

Following the log of a specific container
```bash
sudo docker-compose logs -f server
```

Getting a shell in a container
```bash
sudo docker-compose exec -i -t server /bin/bash
```

Stopping containers and cleaning up
```bash
sudo docker-compose down --volumes
```