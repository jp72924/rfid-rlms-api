# Heimdall - RFID Lock Management System

Heimdall is a Django-based web application designed to manage remote RFID locking systems. It provides a centralized interface for controlling access, managing user accounts, and monitoring hardware status via a web interface.

## Overview

It is built with Django and uses an Anaconda environment to manage dependencies. This documentation walks you through the steps to get the project running on your local machine, run tests, and deploy it to a production server.

## Prerequisites

Before you begin, make sure you have the following installed on your system:

- **Git** – to clone the repository.
- **Anaconda or Miniconda** – to create the Python environment (the project uses Conda for dependency management). 
Download from [https://www.anaconda.com/docs/getting-started/miniconda/main](https://www.anaconda.com/docs/getting-started/miniconda/main "https://www.anaconda.com/docs/getting-started/miniconda/main")

> **Note:** If you are on Linux or macOS, you may need to adjust the environment or create a new one manually (see Troubleshooting).

## Installation

Follow these steps to set up the project on your local machine.

#### 1. Clone the repository

Open a terminal (Anaconda Prompt on Windows) and run:

```bash
git clone https://github.com/jp72924/rfid-rlms-api.git
cd rfid-rlms-api
```

#### 2. Create the Conda environment

The repository includes an environment.yml file that lists all required dependencies. Create a new Conda environment from this file:

```bash
conda env create -f environment.yml
```

#### 3. Activate the environment

Your terminal prompt should show `(heimdall)` indicating the environment is active.

```bash
conda activate heimdall
```

#### 4. Apply database migrations

Django uses migrations to set up the database schema. Run the following commands:

```bash
python manage.py makemigrations webapp
python manage.py migrate
```

- `webapp` is the name of the Django app (adjust if the app name is different; check the webapp folder exists).

- The migrate command applies all migrations to the default SQLite database (a file named `db.sqlite3` will be created in the project root).

#### 5. Create a superuser

To access the admin interface, you need a superuser account:

```bash
python manage.py createsuperuser
```

You will be prompted to enter a username, email address, and password.

#### 6. Run the development server

Start the built‑in Django development server:

```bash
python manage.py runserver 0.0.0.0:8000
```

This makes the server accessible from your machine at [http://127.0.0.1:8000](http://127.0.0.1:8000 "http://127.0.0.1:8000") and also from other devices on your network (if needed).

#### 7. Access the application

Open your web browser and go to [http://127.0.0.1:8000/accounts/login](http://127.0.0.1:8000/accounts/login "http://127.0.0.1:8000/accounts/login")

Log in with the superuser credentials you created.

## Troubleshooting

#### 1. Conda environment creation fails on Linux/macOS

Manually create a new environment with the required packages:

```bash
# Create the environment
conda create -n heimdall

# Activate it
conda activate heimdall

# Install Django and WeasyPrint
conda install -c conda-forge django weasyprint
```

#### 2. Port 8000 already in use

Change the port when running the development server:

```bash
python manage.py runserver 0.0.0.0:8080
```

#### 3. Migration errors

If you get errors about missing tables or conflicting migrations, try:

- Delete the `db.sqlite3` file (if you don't mind losing data) and run `migrate` again.
- Ensure you have run `makemigrations` for the correct app.

## Additional resources

- [Django documentation](https://docs.djangoproject.com/ "Django documentation")
- [Conda user guide](https://docs.conda.io/projects/conda/en/latest/user-guide/ "Conda user guide")

If you encounter any problems not covered here, please open an issue on the [Github Repository](https://github.com/jp72924/rfid-rlms-api/issues "Github Repository").