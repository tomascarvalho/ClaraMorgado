# ClaraMorgado

I've created this website for my mother to display her paintings.
It features an admin platform so she can add, edit and delete the paintings as she pleases.

### Installation

This application requires [Python3](https://www.python.org) to run.
It also requires you to have a [PostgreSQL](http://postgresql.org) database and an [Amazon Aws](http://aws.amazon.com) account.
You should also have [Pip](https://pypi.python.org/pypi/pip) and [VirtualEnv](https://virtualenv.pypa.io/en/stable/) installed.


After installing [Pip](https://pypi.python.org/pypi/pip) and [VirtualEnv](https://virtualenv.pypa.io/en/stable/) you should clone this project:

```sh
$ git clone https://github.com/tomascarvalho/ClaraMorgado.git
```

You should then create a virtual environment and activate it, inside the project folder:

```sh
$ virtualenv venv
$ source venv/bin/activate
```
After this, you should use [Pip](https://pypi.python.org/pypi/pip) to install all the needed dependencies:

```sh
$ pip install -r requirements.txt
```
You can use ```deactivate```to leave the virtual environment.

### Configuration

There are two configuration files provided, inside the ```config```folder:
- ```config.py```is the main configuration file, expecting you to have some environment variables setted up.
This is the file you're expected to use in production.
- ```config_development.py```is the file we're using for development, as it doesn't require us to set environmental variables. We just need to set the needed values accordingly and replace the ```config.config``` imports with ```config.config_development``` imports. If for some reason you are forking this repo, remember not to push this file with secret keys in plain text.

### Run

To start the application just run the following command:
```sh
$ python application.py
```
The application should now be running at ```localhost:5000```and the admin platform at ```localhost:5000/admin```.
