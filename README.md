# Twitter Memories
Twitter Memories is a service that uses your Twitter archive to provide you with a daily view of tweets you have made on the same day, in the past. It's a simple application that allows users to register, upload their twitter archive, and login every day to view their past tweets. 
 

**Technologies Used:** Flask, Python3, Celery, RabbitMQ, Google Cloud Platform, SQLite, SQLAlchemy ORM.

This repo covers the backend, if you want to take a look at the React frontend, it's [here](https://github.com/Gustavo-Cornejo/twitter_memories_webapp).


## Backend Architecture 
This applciation is driven by the Twitter archives that are provided by the users, therefore, I had to build the architecture around a background job that would process the data in the archives. 

### Flask REST Web Server 
The first component is a simple Flask web server that would house both the Authentication/Authorization logic as well as the business logic. It's main purpose is to serve API endpoints for the frontend to interact with, allowing users to:
* Login/Register 
* Grant Resource Authorization
* Upload Twitter Archive 
* Get Tweets 

### Celery Workers & RabbitMQ
When a user uploads their Twitter Archive, a background job is queued in a RabbitMQ instance and ultiamtely consumed by a seperate Server that is running Celery workers. The background job grabs a user's Twitter archive and extracts the relevant information for each tweet and persists it in a database. As of now, the configuration is very static as there's only a single instance of each component here, but with this design we can scale the amount of consumers if we were to have a sudden spike in queued background jobs. 

### Storage: Google Cloud Platform & SQLite Database
I decided to leverage Google Cloud Platform's Storage service to temporarily store user's Twitter Archives until they are ultimately processed and deleted by the backgorund job. To store Users and Tweets, currently I use a single SQLite database with fairly simple schemas.

**Users**
* user id
* username
* hashed password
* file status
* one to many relationship to Tweets

**Tweet** (composite index user id + month)
* tweet id
* user id 
* month 
* day

### Upcoming work
This project is actively being worked on and will continue to be improved on each iteration. Currently some of the work that needs to be done is surrounding cleaning up the code as the beta release is coming up.

