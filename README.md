# Student Management System

A beginner-friendly student record application built for **DevOps Experiment No. 10**. It demonstrates a small end-to-end workflow using Git, GitHub, GitHub Actions, automated tests, and Docker.

## Objectives and features

- Add a student using a name and unique roll number.
- View all saved students in a responsive table.
- Delete a student record.
- Validate required fields, length limits, and duplicate roll numbers.
- Store records in SQLite so they survive application restarts.
- Provide a JSON health check at `/health`.
- Run tests against a separate temporary database.
- Automatically test the application and build its Docker image in GitHub Actions.

## Technologies

| Area | Technology |
| --- | --- |
| Frontend | HTML and CSS |
| Backend | Python 3.12 and Flask |
| Database | SQLite |
| Testing | Pytest |
| Version control and hosting | Git and GitHub |
| Continuous integration | GitHub Actions |
| Containerization | Docker |

## Project structure

```text
student-management-system/
├── app.py
├── requirements.txt
├── requirements-dev.txt
├── render.yaml
├── Dockerfile
├── .dockerignore
├── .gitignore
├── README.md
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── tests/
│   └── test_app.py
└── .github/
    └── workflows/
        └── ci.yml
```

## Requirements

- Python 3.10 or newer (the CI and Docker image use Python 3.12).
- Git.
- Docker Desktop for Windows, with its Linux container engine running, for Docker steps.
- A GitHub account and an empty GitHub repository for the optional GitHub steps.

## Run locally on Windows

Open PowerShell or the VS Code terminal and change to the project folder:

```powershell
cd "C:\Users\chava\OneDrive\Desktop\Agile project\student-management-system"
```

Create and activate a virtual environment, then install dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

If PowerShell blocks activation, use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

Start the application:

```powershell
python app.py
```

Open <http://127.0.0.1:5000>. The local SQLite database is created at `instance/students.db` the first time the application runs. Check its health endpoint at <http://127.0.0.1:5000/health>; it should return `{"status":"healthy"}`.

Stop the local server with **Ctrl+C** in the terminal.

## Run automated tests

Activate the virtual environment if it is not already active, then run:

```powershell
python -m pytest -v
```

The app fixture in `tests/test_app.py` sets the database to a file inside Pytest's temporary directory. Tests therefore do not use or modify `instance/students.db`.

## Build and run with Docker

Build the image from the project folder:

```powershell
docker build -t student-management-system:latest .
```

Create a named volume and start the container:

```powershell
docker volume create student-data
docker run -d --name student-management-app -p 5000:5000 -v student-data:/data student-management-system:latest
```

The `student-data` Docker volume is mounted at `/data`; SQLite uses `/data/students.db` inside the container. This keeps records when the container is stopped, removed, and recreated with the same volume.

Open <http://localhost:5000> to use the app. Check container health manually using:

```powershell
Invoke-RestMethod http://localhost:5000/health
```

## Deploy to Render

The included `render.yaml` configures a Python web service with Gunicorn, a generated secret key, and a health check. To deploy:

1. Create a GitHub repository and add the contents of this project folder to it.
2. Create a Render account, choose **New > Blueprint**, and connect that GitHub repository.
3. Review the detected `student-management-system` service and select **Deploy**.

The free web service uses temporary storage. Student records can be lost when the service restarts or is redeployed, and the service may spin down when idle. Use persistent storage and a suitable paid plan before relying on it for real student records.

View logs and stop/remove the container:

```powershell
docker logs student-management-app
docker stop student-management-app
docker rm student-management-app
```

To start it again after removing the old container, rerun the `docker run` command with the same `student-data` volume. The volume itself is not removed by these commands.

## GitHub Actions CI

The workflow is at `.github/workflows/ci.yml`. It runs on pushes to `main` and on pull requests targeting `main`. It checks out the source, configures Python, installs application and test dependencies, runs Pytest, and builds (but does not publish) the Docker image. A failing test or Docker build fails the workflow.

To check the pipeline:

1. Push the project to the `main` branch of a GitHub repository, or open a pull request targeting `main`.
2. Open the repository on GitHub and select **Actions**.
3. Select **Student Management System CI** and open the latest run.
4. Confirm that **Run automated tests** and **Build Docker image** have green check marks. Open a failed step to view its logs.

No secrets or GitHub Actions variables are required for this workflow.

## Upload this project to GitHub (optional)

First create a new **empty** repository on GitHub. Do not initialize it with a README, license, or `.gitignore`, because this project already has those files. Then run these commands from the project directory. Replace `<your-username>` with your GitHub username and `<repository-name>` with the repository name you chose.

```powershell
cd "C:\Users\chava\OneDrive\Desktop\Agile project\student-management-system"
git init
git add .
git commit -m "Add Student Management System DevOps project"
git branch -M main
git remote add origin https://github.com/<your-username>/<repository-name>.git
git push -u origin main
```

GitHub may ask you to authenticate through a browser or Git Credential Manager. The push is an optional step; do not run it unless you want to publish the code to your repository.

## Optional public deployment

Deployment is not performed as part of this experiment. If your instructor requires a public demo, one option is a Docker-capable hosting provider such as Render:

1. Push the repository to GitHub using the optional steps above.
2. In the hosting provider, create a new web service from that repository and select its Docker deployment option.
3. Configure the service to listen on port `5000`.
4. Add a persistent disk mounted at `/data`. The app stores its SQLite database at `/data/students.db` in the container; without persistent storage, data may be lost when an instance is replaced.
5. Set a strong `SECRET_KEY` environment variable in the provider's private settings, then deploy and test `/` and `/health`.

Availability, pricing, disk support, and provider settings can change. Verify these details with the provider before using it. Do not use the built-in development server for a production system; this small teaching example uses it to stay easy to run locally and in the experiment's container.

## Screenshot checklist for practical evaluation

Capture screenshots on your own machine; no screenshots are generated by the project:

1. **Application page:** show the app in a browser at `http://127.0.0.1:5000`.
2. **Student records:** add one or two sample students and capture the table.
3. **Validation:** try a blank field or duplicate roll number and capture the visible error message.
4. **Health check:** open `http://127.0.0.1:5000/health` and capture the JSON response.
5. **Tests:** run `python -m pytest -v` in VS Code and capture the passing test summary.
6. **Docker:** run `docker ps` and capture the container and port mapping; optionally show the GitHub Actions green run.

Use fictional sample student details in screenshots. Arrange the browser and terminal so the relevant result is readable, and avoid including private information or unrelated desktop content.

## DevOps workflow (viva)

1. **Code:** Build the Flask application, HTML/CSS interface, and SQLite data layer.
2. **Version control:** Git records changes; GitHub stores the shared repository.
3. **Continuous integration:** A push to `main` or pull request to `main` starts GitHub Actions.
4. **Automated verification:** CI installs dependencies and runs Pytest against an isolated test database.
5. **Container build:** If tests pass, CI builds the Docker image. The workflow does not publish or deploy it.
6. **Run consistently:** Docker packages the app and its dependencies; a mounted volume keeps SQLite data outside the disposable container.

This is a CI pipeline: it automatically tests and builds the application. Publishing an image and continuous deployment are separate steps and are intentionally not configured here.
