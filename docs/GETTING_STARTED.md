# Getting started — install and verify the tools

Start with Git and an editor so you can clone the repo and contribute. Install Docker to run the pipeline when the infrastructure owner adds `compose.yaml`. Allow a few minutes for the first image downloads.

| Tool | What you use it for | How you get it |
| --- | --- | --- |
| Git and a GitHub account | Clone, commit, push and review PRs | Install Git. Create or sign in to your GitHub account in a browser. |
| Visual Studio Code or your preferred editor | Edit code, SQL and Markdown | Install your preferred editor. |
| Docker Engine and Docker Compose | Start the shared services locally | Docker Desktop includes both. Linux users can use Docker Engine with the Compose plugin. |
| Apache Kafka | Topics carrying raw, cleaned and rejected reports | Docker image pulled by Compose. |
| Apache NiFi | Visual ETL flow builder and Kafka consumer/producer | Docker image pulled by Compose. Open its UI in your browser. |
| Apache Spark and its Kafka connector | Streaming calculations | Spark runs in a container. The Spark owner pins the matching connector. |
| PostgreSQL | Database and SQL verification | Docker image pulled by Compose. Use the container's SQL client. |
| Python and Java | Producer, PySpark and JVM services | Use the project containers for the agreed runtime versions. Ask the component owner for local runtime versions if developing outside Docker. |

## 1. Git and GitHub

1. **Windows.** Download [Git for Windows](https://git-scm.com/install/win), install it with the default options, and open a fresh Command Prompt. Keep Git Credential Manager enabled if offered.
2. **macOS or Linux.** Use the [official Git installation instructions](https://git-scm.com/install/) for your platform. In Terminal, check the install with the command below.

```bash
git --version
git config --global user.name "Your Name"
git config --global user.email "your-github-email@example.com"
git config --global --get user.name
git config --global --get user.email
```

Replace the example name and email. You can find your GitHub-provided private commit email under [GitHub email settings](https://github.com/settings/emails). Use the same GitHub account that received the team repo invitation. When Git Credential Manager opens the browser on your first push, sign in with that account. If you can clone but get a 403 on push, verify the account and that you accepted the invitation.

## 2. Editor

Download [Visual Studio Code](https://code.visualstudio.com/Download) for your operating system if you need an editor. Open it and choose **File → Open Folder** after cloning. Select the project folder. The built-in editor and terminal are enough to get started.

## 3. Docker and Compose

- **Windows.** Follow [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/). Check the site's WSL 2 and virtualization prerequisites. Use the WSL 2 backend, start Docker Desktop, and wait for the engine to be ready. If WSL is the setup blocker, check `wsl --status` and follow the linked Docker prerequisites, then reopen your terminal.
- **macOS.** Follow [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/). Choose the Apple silicon or Intel installer that matches **About This Mac** and start Docker Desktop.
- **Linux.** Choose your distribution in the [Docker Engine install guide](https://docs.docker.com/engine/install/) and follow the [Compose plugin install guide](https://docs.docker.com/compose/install/linux/), or use Docker Desktop for Linux. Start the Docker service or app before the checks below.

Run these commands in a fresh terminal:

```bash
docker --version
docker compose version
docker info
docker run --rm hello-world
```

The first two commands confirm the clients are installed. `docker info` should show the server, and the last command should print **Hello from Docker!**. If Docker cannot connect on Windows or macOS, open Docker Desktop and wait for the engine. On Linux, check that the service is running and your user can access it. The test image requires an internet connection.

## 4. Clone and open the project

Follow the [README commands](../README.md#start-your-first-task), then open [your team issue](../TEAM.md). Git, Docker, and the editor checks can be done now. The infrastructure owner will add the Compose commands, broker addresses and NiFi URL here when they are verified. Project services use the Compose setup documented by that owner.

## 5. First check-in

Post your OS and whether Git and Docker worked on your assigned issue. Include exact error text if a check fails. Share a scrubbed error message if it contains a token, password or private path.
