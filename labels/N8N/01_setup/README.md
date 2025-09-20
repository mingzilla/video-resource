# n8n Version Control Setup

This project is set up to use a version-controlled workflow for n8n, where workflows and credentials are treated as files that can be committed to Git.

## Goals

- **Workflows as Code:** Workflows are stored as JSON files in the `./workflows` directory, allowing them to be version controlled with Git.
- **Credentials as Code:** Credentials are stored as a JSON file in the `./config` directory. This file is encrypted, but you can git-ignore it for extra security
- **No Additional CLI Tools:** The setup uses the `n8n-cli` tool that is already included in the n8n Docker image. No additional CLI tools need to be installed.
- **Import/Export Workflow:** The `./scripts/import.sh` and `./scripts/export.sh` scripts are used to import and export workflows and credentials to and from the n8n container.
- **Stateless Container:** The n8n container is stateless. It is started from a clean state every time, and the workflows and credentials are imported on startup.
- **No Login:** The n8n UI is directly accessible without a login or account setup page.

## Usage

1. **Start n8n:** Run the `./start.sh` script to start the n8n container and import the workflows and credentials.
2. **Make Changes:** Make changes to your workflows in the n8n UI.
3. **Export Changes:** Run the `./scripts/export.sh` script to export your changes to the `./workflows` and `./config` directories.
4. **Commit Changes:** Commit the changes in the `./workflows` directory to Git.
5. **Import Changes:** You can also run the `./scripts/import.sh` script while n8n is running to sync your workflows and credentials into the system. This is useful if you have made changes to your workflows in your local editor and want to sync them to the running n8n instance without having to restart the container.

## Skip Login

The n8n container uses a pre-configured image (`mingzilla/n8n_no-auth`) that bypasses the setup screen. To rebuild with new n8n releases:

1. **Switch to base image:** Uncomment line 3 and comment line 4 in `docker-compose.yml`
2. **Start and setup:** Run `./start.sh`, complete the setup at http://localhost:5678/setup
3. **Commit and publish:** Run `./scripts/docker-commit-and-publish.sh` to create a new tagged image
4. **Update compose:** Switch back to the new tagged image in `docker-compose.yml`
