# User Contact Management APP
This is Django project that provides an API for managing contacts and users. It is built JWT authentication, and integration with PostgreSQL, Redis, MongoDB, and Celery. The entire application is containerized with Docker.

## Features

-   **User Management**:
    -   Custom User Model using Django's `AbstractBaseUser`.
    -   Contact Model in this project.
    -   Secure JWT-based authentication (Register, Login).
    -   User and Contacts profile management (view and update, get, delete user and contact details).
-   
-   **API**:
    -   **Filtering & Searching**: Search by name/email and filter for upcoming birthdays.
    -   **API Documentation**: API documentation with Swagger (drf-yasg).
-   **Asynchronous Tasks**:
    -   **Celery & Redis**: Celery is used for running background tasks.
    -   **Birthday Reminders**: Celery task runs daily to check for upcoming birthdays and sends reminder emails to users via SMTP.
-   **Logging**:
    -   **MongoDB**: All actions (user registration, profile updates, contact CRUD) are logged to a MongoDB database.
    -   **Log Deletion**: An admin-only API endpoint to archive old logs to a file and delete them from the database.
-   **Performance**:
    -   **Redis**: Caches user and contact lists to retrive details fast.
-   **Deployment**:
    -   **Docker & Docker Compose**: The entire application is on Docker.
    -   **Environment Variables**: Securely manages all credentials and settings using a `.env` file.

## Project Setup and Installation

### Installation Steps

1.  **Clone the Repository**

    ```bash
    git clone <your-repository-url>
    cd usermanagement
    ```
2.  **Install all dependencies from requirements.txt File**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Create the Environment File**

    Create a `.env` file in the project root by copying the example. This file will store all your secret keys and configuration variables.

    ```bash
    cp .env.example .env
    ```

    ```dotenv
    # .env file
    SECRET_KEY=''

    # Database Configuration (PostgreSQL)
    POSTGRES_USER =
    POSTGRES_PASSWORD =
    POSTGRES_DATABASE_NAME =

    # token generator secret key
    JWT_SECRET_KEY =
    JWT_ALGORITHM =

    # Redis
    REDIS_URL=

    # MongoDB Configuration (for Logging)
    MONGO_URL=
    MONGO_DB_NAME=

    # Email Configuration
    SENDGRID_API_KEY =
    EMAIL_BACKEND =
    EMAIL_HOST =
    EMAIL_PORT =
    EMAIL_USE_TLS =
    EMAIL_HOST_USER =
    EMAIL_HOST_PASSWORD =
    EMAIL_FROM =
    ```

3.  **Build and Run with Docker Compose**

    This single command will build the Docker images for all services and start the entire application stack.

    ```bash
    docker-compose up --build
    ```

4.  **Apply Database Migrations**

    ```bash
    python3 manage.py makemigrations
    python3 manage.py migrate
    ```

## Exploring the API

Once the application is running, you can access the following:

-   **API Documentation (Swagger UI)**: `http://localhost:8000/swagger/`
