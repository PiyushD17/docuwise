# Terraform

* Set env vars for TenantID; SubscriptionID, SP Client ID, SP Secret

* Allow Terraform to create role assignments (RBAC): Your Service Principal currently has Contributor. That’s not enough to create role assignments; you need User Access Administrator (or Owner) at the scope where you’re assigning roles (subscription or the RG).

```t
Azure Portal → Subscriptions → your subscription → Access control (IAM) → Add role assignment

Role: User Access Administrator (or Owner, if you’re comfortable)

Assign to: your app registration (the SP you created)

Save
```

## bootstrap project (creates terraform’s remote state storage)

### Bootstrap (creates state RG + Storage + Container)
* `terraform -chdir=infra-bootstrap init    # downloads provider`
* `terraform -chdir=infra-bootstrap apply -auto-approve   # creates RG+SA+container`
* Copy the 4 outputs (RG, account, container, key). OF THE ABOVE COMMAND

```sh
Changes to Outputs:
  + tfstate_account   = "tfst687fc4"
  + tfstate_container = "tfstate"
  + tfstate_key       = "docuwise/infra/terraform.tfstate"
  + tfstate_rg        = "rg-tfstate"
```

```t
Why each file exists (plain English)

versions.tf – declares which Terraform + providers your project needs, and (in the main project) that state should live in Azure Blob.

providers.tf – configures the Azure provider (that features {} line is required).

variables.tf – defines the inputs you can pass (like project, environment, location).

locals.tf – computes helper values (consistent names/suffixes; merges default tags).

main.tf – core “foundational” resources (RG + Log Analytics).

containerapps.tf – the Container Apps Environment (a cluster-like foundation for Container Apps).

acr.tf – Azure Container Registry to store container images.

storage.tf – Storage Account + uploads container your app will use.

eventhub.tf – Event Hubs namespace + hub + two SAS policies (send/listen).

identities.tf – two user-assigned managed identities + RBAC so API/Worker can access Storage/EH using Azure AD.

outputs.tf – prints handy values (names, connection strings, IDs) after apply.

backend.hcl – parameters telling Terraform where to store its remote state (the blob container created by bootstrap).

env/dev.tfvars – the variable values for your dev environment.
```

## Run the main stack
### Main stack (uses remote state; builds Week-10 infra)
```bash
terraform -chdir=infra state list                             # list everything in state tracked by tf
terraform -chdir=infra init -backend-config="backend.hcl"     # Wire state to Azure Blob
terraform -chdir=infra fmt                                    # Format files (optional)
terraform -chdir=infra validate                               # Check syntax and types
terraform -chdir=infra plan  -var-file="../env/dev.tfvars"    # Preview changes
terraform -chdir=infra apply -var-file="../env/dev.tfvars" -auto-approve   # Create resources
```

* this is shown after the terraform plan step
```sh
Changes to Outputs:
  + acr_admin_pwd              = (sensitive value)
  + acr_admin_user             = (known after apply)
  + acr_login_server           = (known after apply)
  + api_identity_client_id     = (known after apply)
  + container_apps_environment = "cae-docuwise-dev"
  + eventhub_conn_listen       = (sensitive value)
  + eventhub_conn_send         = (sensitive value)
  + eventhub_name              = "docuwise-ingest"
  + eventhub_namespace         = "ehns-docuwise-dev"
  + location                   = "westeurope"
  + resource_group             = "rg-docuwise-dev"
  + storage_account_name       = "st26f3d6"
  + storage_primary_connection = (sensitive value)
  + storage_uploads_container  = "uploads"
  + worker_identity_client_id  = (known after apply)
```

* Outputs after apply step

```sh
Outputs:
acr_admin_pwd = <sensitive>
acr_admin_user = "acr26f3d6"
acr_login_server = "acr26f3d6.azurecr.io"
api_identity_client_id = "fb6d0baf-a657-4b10-80c4-f0c5500759c4"
container_apps_environment = "cae-docuwise-dev"
eventhub_conn_listen = <sensitive>
eventhub_conn_send = <sensitive>
eventhub_name = "docuwise-ingest"
eventhub_namespace = "ehns-docuwise-dev"
location = "westeurope"
resource_group = "rg-docuwise-dev"
storage_account_name = "st26f3d6"
storage_primary_connection = <sensitive>
storage_uploads_container = "uploads"
worker_identity_client_id = "7d6dd9e7-093a-49f4-aeb8-e4028386e0b1"
```

* the chat secrets came from dev.tfvars, but everything else was sourced from resources Terraform created (or computed) inside your stack. Terraform builds a dependency graph and then fills in attributes from those resources as soon as Azure returns them.

* Here’s exactly where each Key Vault secret’s value came from in your keyvault.tf

| Key Vault secret name                 | HCL source                                                                   | Where that value really comes from                                                                        |
| ------------------------------------- | ---------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `azure-openai-chat-endpoint`          | `value = var.aoai_chat_endpoint`                                             | You set it in `env/dev.tfvars` (East US 2 AOAI chat endpoint).                                            |
| `azure-openai-chat-api-key`           | `value = var.aoai_chat_api_key`                                              | You set it in `env/dev.tfvars` (East US 2 AOAI key).                                                      |
| `azure-openai-chat-deployment`        | `value = var.aoai_chat_deployment`                                           | You set it in `env/dev.tfvars` (your chat deployment name).                                               |
| `azure-openai-chat-api-version`       | `value = var.aoai_chat_api_version`                                          | You set it in `env/dev.tfvars` (API version for chat).                                                    |
| `azure-openai-endpoint`               | `value = azurerm_cognitive_account.aoai.endpoint`                            | **Provider-computed**: the endpoint of your **West Europe** Azure OpenAI resource that Terraform created. |
| `azure-openai-api-key`                | `value = azurerm_cognitive_account.aoai.primary_access_key`                  | **Provider-computed**: the primary key of that West Europe AOAI resource returned by Azure.               |
| `azure-openai-embeddings-endpoint`    | `value = azurerm_cognitive_account.aoai.endpoint`                            | Same as above (West Europe AOAI endpoint).                                                                |
| `azure-openai-embeddings-api-key`     | `value = azurerm_cognitive_account.aoai.primary_access_key`                  | Same as above (West Europe AOAI key).                                                                     |
| `azure-openai-embeddings-deployment`  | `value = var.aoai_embeddings_deployment`                                     | You set default in `variables.tf` (or override in `dev.tfvars`).                                          |
| `azure-openai-embeddings-api-version` | `value = var.aoai_embeddings_api_version`                                    | You set default in `variables.tf` (or override in `dev.tfvars`).                                          |
| `eventhub-connection-send`            | `value = azurerm_eventhub_authorization_rule.send.primary_connection_string` | **Provider-computed**: SAS connection string Azure returns for your Event Hub **send** rule.              |
| `storage-connection-string`           | `value = azurerm_storage_account.data.primary_connection_string`             | **Provider-computed**: Storage account connection string Azure returns for your app SA.                   |

* A few important mechanics behind the scenes:

* Implicit dependencies. When a secret references azurerm_cognitive_account.aoai.endpoint, Terraform knows the Key Vault secret must be created after the Cognitive Account exists. That’s why you don’t need to write depends_on for everything—references create the DAG for you.
You did add depends_on = [azurerm_role_assignment.tf_kv_admin] to ensure your SP has Key Vault admin before attempting to write secrets. That’s perfect.

* Provider-computed attributes. Things like primary_access_key, endpoint, primary_connection_string, and the Event Hub SAS strings are computed by Azure and returned to Terraform after creation. Terraform then uses those values when creating the KV secrets.

* Variables vs. resources. We used variables for the eastus2 chat because that resource is outside this stack. We used resource attributes for the westeurope embeddings because Terraform created that AOAI resource and thus can read its attributes directly.

* State contains secret values. Any secret value you pass or read via Terraform is stored in the Terraform state (your state is in the Storage Account you bootstrapped). That’s why we: keep the backend private, avoid committing state to git, restrict who can access the state container.

* If you want to avoid having (for example) the eastus2 chat API key in state, a common pattern is: create the KV secret once manually in the Portal, and in Terraform either (a) don’t manage that secret, or (b) manage only its metadata and add lifecycle { ignore_changes = [value] } after the first apply so future applies don’t read/write the value.

* If you want, I can show you that “don’t-track secret value changes” pattern for specific KV secrets, or wire up your Container App next to read these secrets via managed identity and expose them as env vars.
