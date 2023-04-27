# newspaper-api

Deprecated. Migrated to private repository

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
* update `helm-chart/values.yaml` and set image tag value
* `helm diff upgrade --namespace stable newspaper-api . -f values.yaml` to check for what's going to be applied
* `helm upgrade -i --namespace stable newspaper-api . -f values.yaml` to update the deployment with the new tag

## Environment Variables

When fetching urls through newspaper api, CUSTOM_USER_AGENT value is used as user agent header for domains in the CUSTOM_DOMAINS set.
 
* CUSTOM_DOMAINS: List of domain names seperated by space e.g. 'domain1.test domain2.test domain3.test'

* CUSTOM_USER_AGENT: String, e.g. 'Mozilla/5.0'
