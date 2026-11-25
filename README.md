# CompanionHub API

A Flask REST API for creating and managing AI companion profiles.

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

## Environment variables

Copy the environment variable template:

```bash
cp .env.example .env
```

Update the `.env` file with your own configuration.

- `FLASK_CONFIG`: Determines which application environment to use.
- `JWT_SECRET_KEY`: Secret key used to sign and verify authentication tokens.
- `DATABASE_URL`: Connection URL for the application's database.

Generate a secure JWT secret key using:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Never commit your `.env` file or share your secret key.

## Database migrations

This project uses Flask-Migrate and Alembic to manage database schema changes through the Flask CLI.

Set the Flask application:

```bash
export FLASK_APP="companionhub:create_app()"
```

Initialize the migration folder (only if it does not already exist):

```bash
flask db init
```

Generate a migration after creating or updating database models:

```bash
flask db migrate -m "Describe database changes"
```

Apply migrations to the database:

```bash
flask db upgrade
```