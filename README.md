# Bonfire — Discord Bot

Bonfire is a private Discord music bot built with Python and designed as a hands-on DevOps learning project.

It uses **Lavalink** as a standalone audio server and **Kubernetes** to orchestrate its components. Its current functionality allows users to play local audio files by uploading them as Discord message attachments.

The primary goal of this project is to explore and practice containerization, orchestration, configuration management, persistent storage, application logging, and deployment workflows.

## Architecture

Bonfire consists of two main services:

- **Discord Bot:** A Python application built with `discord.py` and `Wavelink`. It receives audio attachments and controls playback.
- **Lavalink:** A standalone audio server responsible for processing and streaming audio to Discord voice channels.

Both services run in separate containers and communicate through an internal Kubernetes Service.

### Playback workflow

1. A user uploads an audio file as a Discord message attachment.
2. The bot checks whether the user is connected to a voice channel.
3. The bot joins the channel and saves the uploaded file to shared persistent storage.
4. Lavalink accesses the same file through the shared volume.
5. Wavelink requests Lavalink to play the track.

### Technology stack

| Component | Technology |
|---|---|
| Programming language | Python 3.14 |
| Discord API | discord.py |
| Lavalink client | Wavelink |
| Audio server | Lavalink 4 |
| Containerization | Docker |
| Main orchestration platform | Kubernetes |
| Local Kubernetes environment | Minikube |
| Manifest management | Kustomize |
| Persistent storage | PersistentVolumeClaim |
| Configuration management | ConfigMaps and Secrets |
| Version control | Git |

## Current features

- Connection to a private Discord server.
- Application command registration and synchronization.
- `/ping` command for basic bot availability checks.
- Audio file uploads through Discord messages.
- Automatic connection to the user's voice channel.
- Local audio playback through Lavalink.
- Logging of relevant application events and operations.

**Current limitations:** Playback is currently focused on local audio files uploaded as Discord attachments. YouTube integration is disabled and is not part of the current working release.

## Project structure

```text
Bonfire/
├── k8s/
│   ├── application.yml
│   ├── audio-startup-service.yaml
│   ├── bot-deployment-def.yaml
│   ├── bot-pod-def.yaml
│   ├── configmap.env
│   ├── kustomization.yaml
│   ├── lavalink-clusterip-service.yaml
│   ├── lavalink-deployment-def.yaml
│   ├── lavalink-pod-def.yaml
│   ├── music-pvc.yaml
│   ├── secrets.env.example
│   └── .gitignore
├── local-music/
│   └── .gitkeep
├── .dockerignore
├── .gitattributes
├── .gitignore
├── compose.yaml
├── config.env.example
├── Dockerfile
├── main.py
└── requirements.txt
```

The `bot-pod-def.yaml` and `lavalink-pod-def.yaml` files are retained as learning examples of individual Pod definitions. The main deployment uses Kubernetes Deployments instead.

## Running your own Bonfire instance

Bonfire is designed to be deployed with your own Discord application and credentials.

**Do not use someone else's bot token or invitation link.** Each deployment should have its own Discord application, bot account, credentials, and server installation.

### 1. Create your Discord application

1. Open the [Discord Developer Portal](https://discord.com/developers/applications).
2. Create a new application.
3. Open the **Bot** section and create or configure its bot account.
4. Enable the **Message Content Intent** under Privileged Gateway Intents.
5. Generate a bot token and store it securely.

For a private deployment, configure the installation settings to use **Guild Install**. Select the required OAuth2 scopes (`bot` and `applications.commands`) and grant the permissions needed by Bonfire:

- View Channels
- Send Messages
- Connect
- Speak
- Use Application Commands

Generate your own installation URL using your application's OAuth2 settings. Do not reuse or publish another deployment's invitation URL.

### 2. Configure environment variables

The bot reads its credentials and connection settings from environment variables. You do not need to modify `main.py` to configure your own Discord token or Lavalink connection.

For Kubernetes, create your secrets file from the provided example:

```bash
cp k8s/secrets.env.example k8s/secrets.env
```

Edit `k8s/secrets.env`:

```dotenv
DISCORD_BOT_TOKEN=your_discord_bot_token
LAVALINK_PASS=your_lavalink_password
```

For Docker Compose, create the corresponding configuration file:

```bash
cp config.env.example config.env
```

Add your own credentials and configuration values there.

**Never commit `config.env` or `k8s/secrets.env` to version control.** Both files are excluded through Git ignore rules.

## Kubernetes deployment

Kubernetes is the primary deployment method for this project.

### Prerequisites

- Docker
- kubectl
- Minikube
- Git
- A Discord application and bot token

### 1. Clone the repository

```bash
git clone https://github.com/danmbel15/Bonfire.git
cd Bonfire
```

### 2. Configure Kubernetes secrets

Create and edit the secrets file as described in the previous section:

```bash
cp k8s/secrets.env.example k8s/secrets.env
```

Make sure the variable names match the ones expected by the Kubernetes manifests.

### 3. Review the application configuration

The `k8s/configmap.env` file contains non-sensitive configuration values:

```dotenv
LAVALINK_URI=http://audio:2333
LAVALINK_PORT=2333
LAVALINK_ADDRESS=0.0.0.0
MUSIC_PATH=/music
```

Lavalink's configuration is stored in `k8s/application.yml`.

Kustomize uses `configMapGenerator` and `secretGenerator` to create the corresponding Kubernetes resources from these files.

### 4. Start Minikube

```bash
minikube start
```

Check that the cluster is running:

```bash
kubectl get nodes
```

### 5. Build the bot image

Build the bot image in Minikube's Docker environment:

```bash
minikube image build -t bonfire-bot:0.1.12 .
```

The image tag must match the one declared in `k8s/bot-deployment-def.yaml`.

The manifests use `imagePullPolicy: IfNotPresent`, allowing Kubernetes to use the locally available image.

### 6. Validate and apply the manifests

Preview the resources generated by Kustomize:

```bash
kubectl kustomize k8s/
```

Apply the configuration:

```bash
kubectl apply -k k8s/
```

### 7. Verify the deployment

Check Pods, Services, and PersistentVolumeClaims:

```bash
kubectl get pods
kubectl get services
kubectl get pvc
```

Follow the bot logs:

```bash
kubectl logs -f deployment/bot-deployment
```

Follow the Lavalink logs:

```bash
kubectl logs -f deployment/lavalink-deployment
```

The bot Deployment includes an init container that waits for Lavalink to respond before starting the main application container. Lavalink also uses a readiness probe to report its availability to Kubernetes.

### 8. Test playback

1. Invite your own bot application to your Discord server.
2. Wait until both Pods are running and their containers are ready.
3. Join a voice channel.
4. Upload a supported audio file as a Discord message attachment.
5. Verify that the bot joins the channel and starts playback.

## Persistent storage

Bonfire uses a `PersistentVolumeClaim` named `bonfire-music` to share audio files between the two services.

- The bot mounts the volume at `/music` with read-write access.
- Lavalink mounts the same volume at `/music` with read-only access.

The PVC uses the `ReadWriteOnce` access mode. This configuration works in the current Minikube setup, where both Pods can access the storage from the same node.

A multi-node deployment may require a different storage solution that supports shared access, such as `ReadWriteMany`, depending on the infrastructure provider.

## Alternative deployment with Docker Compose

The repository also includes `compose.yaml` as an alternative way to run the services without Kubernetes.

Create the environment file:

```bash
cp config.env.example config.env
```

Configure your credentials and start the services:

```bash
docker compose --env-file config.env up --build -d
```

Check the running services:

```bash
docker compose --env-file config.env ps
```

Follow the logs:

```bash
docker compose --env-file config.env logs -f
```

Stop the services:

```bash
docker compose --env-file config.env down
```

## Logging and troubleshooting

The bot uses Python's built-in `logging` module to record relevant application events, including:

- Lavalink node connection and disconnection events.
- Audio service availability events.
- Audio file reception and processing.
- Information useful for diagnosing runtime issues.

Python output is configured to be unbuffered inside the container, allowing logs to be viewed promptly through `kubectl logs` or Docker Compose.

## Security considerations

Sensitive files include:

- `config.env`
- `k8s/secrets.env`

Example configuration files are provided to document the required environment variables without exposing real credentials.

---

**Repository:** https://github.com/danmbel15/Bonfire
