
![Logo](./app/static/img/logo.png)

# FlightAlert - Push Notifications for flight events

**Never miss special aircrafts at your favorite airport:**

Flight alert is an open-source flight notification web service which allows you to reicieve alerts for selected aircrafts arriving or departing at your local airport. 

It is based on a [Flask](https://flask.palletsprojects.com) web framework and the Google [Firebase Messaging](https://firebase.google.com/docs/cloud-messaging) api.


## Features

- Complete website with user registration and email confirmation with the gmail api
- Search airports with the [Air Labs api](https://airlabs.co/)
- Aircraft database with over 1200 aircrafts
- Receive push notifications on multiple devices
- Ready to be deployed in a [Docker](https://www.docker.com/) container
- Running on gunicorn WSGI HTTP Server
## How it works

Airport schedules are checked every day on the FlightAware website. The user can add multiple airports and different aircraft models for each one. 

When an aircraft that a user has added to their watch list takes off or lands at that airport, the user will receive a push notification on their device.
## Environment Variables

To run this project, you will need to add the following environment variables to your docker container:

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| [`SECRET_KEY`](https://stackoverflow.com/a/54433731) | `string` | **Required**. Flask application secret key |
|`SQLALCHEMY_DATABASE_URI`|`string`|**Required**. Database path|
|`AIR_LABS_API_KEY`|`string`|**Required to search airports**. You can get a free key on their website|
|`FLIGHTAWARE_USERNAME`|`string`|**Required**. FlightAware account used for scraping the tables|
|`FLIGHTAWARE_PASSWORD`|`string`|**Required**. FlightAware account password|
|`GOOGLE_APPLICATION_CREDENTIALS`|`string`|**Required**. Path to your firebase service account .json file|
|`OAUTH2_TOKEN`|`string`|**Required**. Path to your oauth credential.json file|
|`SECURITY_PASSWORD_SALT`|`string`|**Required**. Used for hashing user related links|
|`ADMIN_PASSWORD`|`string`|**Optional**. FlightAlert admin password|
|`ADMIN_EMAIL`|`string`|**Optional**. FlightAlert admin mail|

They can also be found in the config.py file.


## Run Locally

Clone the project

```bash
  git clone https://github.com/Foffa0/Flight-Alert.git
```

Go to the project directory

```bash
  cd my-project
```

Install dependencies

```bash
  pip install requirements.txt
```

Start the server (only for development)

```bash
  py run.py
```

A better solution is to run the [gunicorn](https://gunicorn.org/) server as it is much faster and stable than the default flask development server.

```bash
  gunicorn 'app:create_app()' -w 1 --threads 2 -b 0.0.0.0:5000 --access-logfile=-
```

> _**Note:** Gunicorn only runs on UNIX systems


## Run in a docker container

The Dockerfile for creating an Image is provided in the root directory. When creating the container you need to add all the [environment variables](#environment-variables) in order to run this project.