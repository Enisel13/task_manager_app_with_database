# Task Manager

## What I built

A Flask task manager with a web interface and an API for adding, viewing, updating, and deleting tasks. Task data is stored in MySQL. The same application has three deployment options:

1. **Docker Compose (local):** the app and MySQL run as two separate containers on one machine; this is the quickest way to try it.
2. **Kubernetes (local):** the app and MySQL run in a local cluster, demonstrating Deployments, Services, configuration, and persistent storage without Azure. `k8s-local/`
3. **Azure (cloud):** Terraform defines the Azure infrastructure, with AKS running the app, ACR storing its image, Key Vault storing the database password, and managed MySQL Flexible Server hosting the database. Kubernetes manifests in `k8s-aks/` deploy the app. This is the primary infrastructure design; its Terraform project is maintained separately in `task_app_infrastructure/`.

## Azure resources

Terraform creates a resource group and a virtual network with separate subnets for AKS and the private MySQL Flexible Server. It also sets up private DNS for the database and an NSG associated with its subnet.

The remaining resources are the AKS cluster, an ACR for the app image, a Key Vault for the database password, and a managed MySQL server with the `tasks_db` database. A user-assigned identity and federated credentials let the app pod access Key Vault without storing an Azure credential in the pod; role assignments let AKS pull images from ACR and the app read vault secrets. The password itself must be added to Key Vault separately.

At runtime, AKS pulls the app image from ACR, and the pod uses workload identity and the Secrets Store CSI driver to read the password from Key Vault before connecting to MySQL over the private network.

## Running the three options

### Docker Compose (local)

Copy `.env.example` to `.env`, set your local `MYSQL_*` values there (the app's database host should be `mysql`), and do not commit `.env`. The example file contains placeholders and can be committed. Then run from the repository root:

```sh
cp .env.example .env
docker compose up --build
```

Open [http://localhost:5002](http://localhost:5002). Compose publishes MySQL on host port 3306 and keeps its data in a named volume.

**Note:** `database/init.sql` is a MySQL init script. Compose mounts the whole `database/` folder into MySQL's init directory, so MySQL may try to parse this helper as SQL; keep it outside that mount when starting a fresh Compose database.

### Kubernetes (local)

With a local cluster running and `kubectl` configured:

```sh
kubectl apply -f k8s-local/
kubectl port-forward service/task-manager-service 8080:80
```

Open [http://localhost:8080](http://localhost:8080). MySQL storage uses a `hostPath` at `/mnt/data`, so persistence depends on the local cluster.

### Azure

Use an Azure subscription, Azure CLI authentication, Terraform, Docker, and `kubectl` access to AKS. In the separate `task_app_infrastructure/` project, configure inputs and run `terraform init`, `terraform plan`, then review the plan and costs before `terraform apply`. Add the MySQL password to Key Vault as `mysql-password`, build and push the app image to ACR, align the image and Azure settings in `k8s-aks/` with Terraform outputs, then apply those Kubernetes manifests.

The repository also has two manual helper scripts, not an automated CI/CD pipeline: [ci.sh](./ci.sh) builds an image with the supplied tag and pushes it to ACR, while [cd.sh](./cd.sh) is intended to update the image tag in a Kubernetes manifest and apply the manifests. The deployment script currently points to a `k8s/` directory that is not present in the repository, so its path must be updated before use.

After the AKS app pod is running and `kubectl` is connected to that cluster, run this helper from the repository root:

```sh
bash database/init-from-conatiner.sql
```

Despite its `.sql` suffix, the file runs `kubectl exec -i deployment/task-manager-app -- python -` with inline Python inside the app pod. The Python code uses the pod's `MYSQL_*` values to open a one-off connection to MySQL, creates the `tasks` table if needed, and inserts four sample tasks. This prepares the schema/data and verifies that the pod can reach the database; it does not configure the Flask app's connection, which already uses those environment variables for its own requests. Run it only once because repeating it adds duplicate sample tasks.

## What security considerations did you make?

Parameterized SQL and basic input validation reduce common data-handling risks. In Azure, MySQL is placed in a private subnet, and a network security group restricts traffic to that subnet: it allows MySQL traffic from the AKS subnet and blocks inbound Internet traffic. The design also uses private DNS, Key Vault with workload identity, and scoped ACR pull permissions.

## What would you improve if this were a production system?

For production, remove and rotate committed credentials; use least-privilege database access, HTTPS ingress, authentication, backups and tested restores; harden and scan images; and add automated tests, monitoring, and alerting. I would also use GitHub Actions to build a CI/CD pipeline that automates the process from code changes through testing and deployment to production.

## Most difficult part

The hardest part was integrating the Azure services end to end: private DNS/networking for MySQL, AKS image pulls from ACR, and federated workload identity with Key Vault secret delivery. Each has separate configuration and permissions, so keeping Terraform outputs and Kubernetes manifests aligned required the most troubleshooting. I also encountered Azure quota limits and contacted Azure Support to request an increase before I could continue provisioning.
