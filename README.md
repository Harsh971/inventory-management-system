# Cloud-Based Inventory Management System

This project is an end-to-end inventory management system featuring:

- A **Flask API** built with object-oriented design.
- **MySQL** integration with a normalized schema.
- Concurrency control for handling simultaneous orders.
- **Containerization** using Docker and Docker Compose.
- **Kubernetes orchestration** for scalable deployment.
- (Optional) A basic UI that can be further enhanced.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Create and Activate a Virtual Environment](#2-create-and-activate-a-virtual-environment)
  - [3. Install Python Dependencies](#3-install-python-dependencies)
  - [4. Configure Environment Variables](#4-configure-environment-variables)
  - [5. Create the MySQL Database and Tables](#5-create-the-mysql-database-and-tables)
  - [6. Run the Flask Application Locally](#6-run-the-flask-application-locally)
- [Containerization with Docker Compose](#containerization-with-docker-compose)
  - [1. Build and Run Containers](#1-build-and-run-containers)
  - [2. Verify Endpoints](#2-verify-endpoints)
- [Kubernetes Deployment](#kubernetes-deployment)
  - [1. Prerequisites for Kubernetes](#1-prerequisites-for-kubernetes)
  - [2. Using Local Images in Kubernetes](#2-using-local-images-in-kubernetes)
  - [3. Kubernetes YAML Files](#3-kubernetes-yaml-files)
  - [4. Deploying to Kubernetes](#4-deploying-to-kubernetes)
- [Future Enhancements](#future-enhancements)
- [Troubleshooting](#troubleshooting)

---

## Project Overview

This project provides a fully containerized inventory management system with the following core components:

- **API Endpoints:** For adding products, placing orders, and generating inventory reports.
- **MySQL Database:** Stores product details, orders, and order items.
- **Concurrency Management:** Uses thread locks to safely process simultaneous orders.
- **Docker & Docker Compose:** Containerizes both the application and MySQL.
- **Kubernetes Deployment:** YAML files are provided for deploying the system to a Kubernetes cluster.
- **Optional UI:** Basic HTML templates can be enhanced for a complete web interface.

---

## Features

- **Flask API:** RESTful endpoints built with Flask.
- **MySQL Integration:** Well-designed schema for products, orders, and order items.
- **Concurrency:** Ensures safe order processing.
- **Dockerized:** Simple setup with Docker and Docker Compose.
- **Kubernetes Ready:** YAML configurations for cloud or local Kubernetes clusters.
- **Extensible UI:** (Optional) Starter templates using Flask's Jinja2.

---

## Prerequisites

- **Operating System:** Linux, macOS, or Windows.
- **Docker & Docker Compose:** Installed on your system.
- **Kubernetes:** Docker Desktop's integrated Kubernetes or Minikube for local testing.
- **Python 3.8+** and **MySQL** (for local development).

---

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/inventory-management-system.git
cd inventory-management-system
```

### 2. Create and Activate a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate   # On Windows use: venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a file named ``.env`` in the project root with the following content (adjust values as needed):

```bash
DB_USER=inventory_user
DB_PASSWORD=inventory_pass
DB_HOST=127.0.0.1
DB_NAME=inventory_db
SECRET_KEY=your_secret_key
```

### 5. Create the MySQL Database and Tables

- Option 1: Use your MySQL client and run the provided SQL schema (if available).
- Option 2: Uncomment the `db.create_all()` lines in `app.py` temporarily and run the app once to create the tables automatically.

### 6. Run the Flask Application Locally

```bash
python app.py
```
Open your browser at `http://localhost:5000` to verify the server is running. Test endpoints (e.g., `/add_product`, `/report`) using curl, Postman, or a browser.


## Containerization with Docker Compose

### 1. Build and Run Containers

Make sure you have a working `Dockerfile` and `docker-compose.yaml` in the project root. Then run:

```bash
docker-compose up --build
```
This command will:
- Build the Docker image for the Flask app.
- Start the MySQL container.
- Start the Flask app container and link them on the same network.

### 2. Verify Endpoints

- Open `http://localhost:5000` in your browser.
- Test the `/report` endpoint at `http://localhost:5000/report`.
- Use curl/Postman to test API endpoints.


## Kubernetes Deployment

### 1. Prerequisites for Kubernetes
- Docker Desktop with Kubernetes enabled or a local cluster like Minikube.
- Ensure kubectl is installed and configured to interact with your cluster.

### 2. Using Local Images in Kubernetes
Since Docker Desktop's Kubernetes shares the same Docker daemon, you can use the locally built image directly:

#### 1. Build the Image Locally:
```bash
docker build -t inventory-app:latest .
```

#### 2. Reference the Local Image in Your YAML Files:
In your deployment YAML files, set the image to:
```bash
image: inventory-app:latest
```

### 3. Kubernetes YAML Files
MySQL Deployment & Service (`mysql-deployment.yaml`)
```bash
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:5.7
        env:
          - name: MYSQL_ROOT_PASSWORD
            value: "rootpassword"
          - name: MYSQL_DATABASE
            value: "inventory_db"
          - name: MYSQL_USER
            value: "inventory_user"
          - name: MYSQL_PASSWORD
            value: "inventory_pass"
        ports:
        - containerPort: 3306
---
apiVersion: v1
kind: Service
metadata:
  name: mysql-service
spec:
  selector:
    app: mysql
  ports:
    - port: 3306
      targetPort: 3306
  clusterIP: None
```

Flask App Deployment & Service (`inventory-app-deployment.yaml` & `inventory-app-service.yaml`)

```bash
apiVersion: apps/v1
kind: Deployment
metadata:
  name: inventory-app-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: inventory-app
  template:
    metadata:
      labels:
        app: inventory-app
    spec:
      containers:
      - name: inventory-app
        image: inventory-app:latest
        env:
          - name: DB_USER
            value: "inventory_user"
          - name: DB_PASSWORD
            value: "inventory_pass"
          - name: DB_HOST
            value: "mysql-service"
          - name: DB_NAME
            value: "inventory_db"
          - name: SECRET_KEY
            value: "your_secret_key"
        ports:
          - containerPort: 5000
---
apiVersion: v1
kind: Service
metadata:
  name: inventory-app-service
spec:
  selector:
    app: inventory-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 5000
  type: LoadBalancer
```

### 4. Deploying to Kubernetes
Apply the YAML files:
```bash
kubectl apply -f mysql-deployment.yaml
kubectl apply -f inventory-app-deployment.yaml
kubectl apply -f inventory-app-service.yaml
```

Verify your deployments:
```bash
kubectl get pods
kubectl get svc
```

Access your application:
- For LoadBalancer, use the external IP once assigned.
- Alternatively, run port forwarding:
```bash
kubectl port-forward svc/inventory-app-service 5000:80
```

Then visit `http://localhost:5000`.


## Future Enhancements
- User Interface: Develop a comprehensive front-end using frameworks like React or Vue.
- Security: Implement authentication/authorization and manage secrets using Kubernetes Secrets.
- Testing: Add unit, integration, and end-to-end tests.
- Monitoring & Logging: Integrate tools like Prometheus, Grafana, and the ELK Stack.
- CI/CD Pipeline: Automate builds and deployments using GitHub Actions, Jenkins, etc.

## Troubleshooting
- DNS Issues During Build:
If you encounter DNS resolution issues, try disabling BuildKit:
```bash
DOCKER_BUILDKIT=0 docker-compose up --build
```
Or update Docker daemon DNS settings in /etc/docker/daemon.json.

- Database Connection Errors:
Ensure environment variables are correctly set and that MySQL is running.

- Kubernetes Deployment Problems:
Use `kubectl logs <pod-name>` for debugging and verify service configurations.
