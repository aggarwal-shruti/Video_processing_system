# Project - Video Processing System 
## Prerequisites

Ensure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/aggarwal-shruti/Video_processing_system.git
cd Video_processing_system


docker-compose up --build
```

Once the containers are up and running, navigate to:
```
http://localhost:8000
```

Apply the database migrations using the following command:

```
docker-compose exec web python manage.py migrate
```

Create Superuser using 
```
docker-compose exec web python manage.py createsuperuser
```




