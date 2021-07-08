# newspaper-api

Port: 38765


## Usage

- `/topimage` and `/` returns the top image of the link/article in question
 
 args:

 -- `url`: encoded url
 
 returns
 `{
  "topimage": "string",
  "title": "string",
  "text": "string",
  "publish_date": "publishdate",
  "movies": "[]string",
  "images:": "[]string",
  "html": "string",
  "authors": "[]string"
  }`


## Local build & launch
* `git clone https://github.com/Smarp/newspaper-api`
* `docker build -t news .`
* `docker run -p 38765:38765 news:latest`
* open in browser http://localhost:38765/?url=https://smarp.com/

## Deployment
* put a new tag on https://github.com/Smarp/newspaper-api/releases
* wait until new docker image will be available for that tag https://hub.docker.com/r/smarp/newspaper-api/tags (might take 5-30 min)  
* `kubectl diff -f newspaper-api.yml` to check for what’s going to be applied
* `kubectl apply -f newspaper-api.yml` to update the deployment with the new tag
