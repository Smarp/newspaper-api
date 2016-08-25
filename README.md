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
