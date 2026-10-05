# Cloud Microservices Lab – Assessment 1

## 1. Introduction

This assessment demonstrates the development, containerization, deployment, communication, and performance testing of a simple cloud-based microservice application.

The application consists of three independent microservices:

- Student Service
- Course Service
- Enrollment Service

Each service runs independently inside a Docker container and communicates with other services through a Docker bridge network.

The project also includes workload testing and resource monitoring to analyze:

- Response Time
- Throughput
- Failed Requests
- CPU Utilization
- Memory Utilization

---

# 2. Objectives

The main objectives of this assessment are:

1. Develop multiple independent microservices.
2. Containerize each microservice using Docker.
3. Create Docker images for each service.
4. Deploy all services using Docker Compose.
5. Establish communication between microservices.
6. Test the application under different concurrency levels.
7. Measure response time and throughput.
8. Measure CPU and memory utilization.
9. Generate performance graphs.
10. Analyze the performance of the microservice architecture.
11. Organize and upload the complete assessment to GitHub.

---

# 3. Technologies Used

- Python 3.14
- Flask
- Docker
- Docker Compose
- Docker Bridge Network
- Python Requests Library
- Matplotlib
- Git
- GitHub
- Windows PowerShell

---

# 4. System Architecture

The application contains three microservices.

```text
                    Client / Browser
                           |
                           |
                           v
              +------------------------+
              |   Enrollment Service   |
              |       Port 5003        |
              +-----------+------------+
                          |
                 +--------+--------+
                 |                 |
                 v                 v
       +----------------+   +----------------+
       | Student Service|   | Course Service |
       |    Port 5001   |   |    Port 5002   |
       +----------------+   +----------------+
```

## 5. Creating the Three Microservices

Three independent Flask-based microservices were created:

- **Student Service** – provides student information.
- **Course Service** – provides course information.
- **Enrollment Service** – combines information from the Student and Course services.

Each service was developed separately with its own `app.py`, `requirements.txt`, and `Dockerfile`.

## 6. Connecting the Microservices

The three services were connected using a Docker bridge network created through Docker Compose.

The Enrollment Service communicates with the Student Service and Course Service using their Docker service names. This allowed the services to exchange information while running in separate containers.

## 7. Dockerization and Docker Images

Each microservice was containerized using its own Dockerfile. Docker images were built for all three services:

- `student-service:1.0`
- `course-service:1.0`
- `enrollment-service:1.0`

The images were then used to create the respective containers.

## 8. Docker Compose and Deployment

A `docker-compose.yml` file was created to manage all three microservices together.

The services were deployed with:

```powershell
docker compose up -d
```

## 9. Load Testing

A Python load-testing script was created to test the application with different concurrency levels:

**1, 2, 4, 8, and 16 concurrent requests.**

Response time, throughput, and failed requests were recorded for each workload.

## 10. CPU and Memory Monitoring

An automated performance-testing script was created to measure CPU and memory utilization of the three Docker containers while the workloads were running.

The measurements were collected for all five workload levels.

## 11. Final Observation Table

| Workload | Concurrent Requests | Total Requests | Successful | Failed | Avg Response Time (ms) | Throughput (req/s) | Avg CPU (%) | Avg Memory (%) |
|----------|---------------------|----------------|------------|--------|--------------------------|---------------------|-------------|----------------|
| W1 | 1 | 50 | 50 | 0 | 10.90 | 91.17 | 1.87 | 0.69 |
| W2 | 2 | 100 | 100 | 0 | 12.57 | 157.08 | 18.10 | 0.69 |
| W3 | 4 | 200 | 200 | 0 | 16.52 | 238.17 | 15.42 | 0.69 |
| W4 | 8 | 400 | 400 | 0 | 29.95 | 264.81 | 71.03 | 0.71 |
| W5 | 16 | 800 | 800 | 0 | 57.62 | 275.32 | 35.91 | 0.70 |
