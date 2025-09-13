data "azurerm_client_config" "current" {}
# ^ identifies "who" Terraform is (your SP) to grant it Key Vault write access via RBAC.

resource "azurerm_key_vault" "kv" {
  name                = "kv-${local.name_prefix}" # e.g., kv-docuwise-dev
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"

  # Use RBAC instead of Access Policies (modern, cleaner with managed identities)
  enable_rbac_authorization = true

  soft_delete_retention_days = 7
  purge_protection_enabled   = false # dev-friendly; set true for prod
  tags                       = local.tags
}

# Let Terraform's SP write secrets now
resource "azurerm_role_assignment" "tf_kv_admin" {
  scope                = azurerm_key_vault.kv.id
  role_definition_name = "Key Vault Administrator" # allows create/update secrets
  principal_id         = data.azurerm_client_config.current.object_id
}

# App will only need to read secrets at runtime:
resource "azurerm_role_assignment" "api_kv_reader" {
  scope                = azurerm_key_vault.kv.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_user_assigned_identity.api_mi.principal_id
}

resource "azurerm_role_assignment" "worker_kv_reader" {
  scope                = azurerm_key_vault.kv.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_user_assigned_identity.worker_mi.principal_id
}

# Store useful secrets so your apps can KeyVault-reference them later
resource "azurerm_key_vault_secret" "aoai_endpoint" {
  name         = "azure-openai-endpoint" # was AZURE_OPENAI_ENDPOINT
  value        = azurerm_cognitive_account.aoai.endpoint
  key_vault_id = azurerm_key_vault.kv.id
  depends_on   = [azurerm_role_assignment.tf_kv_admin]
}

resource "azurerm_key_vault_secret" "aoai_key" {
  name         = "azure-openai-api-key" # was AZURE_OPENAI_API_KEY
  value        = azurerm_cognitive_account.aoai.primary_access_key
  key_vault_id = azurerm_key_vault.kv.id
  depends_on   = [azurerm_role_assignment.tf_kv_admin]
}

resource "azurerm_key_vault_secret" "eventhub_send" {
  name         = "eventhub-connection-send" # was EVENTHUB_CONNECTION_SEND
  value        = azurerm_eventhub_authorization_rule.send.primary_connection_string
  key_vault_id = azurerm_key_vault.kv.id
  depends_on   = [azurerm_role_assignment.tf_kv_admin]
}

resource "azurerm_key_vault_secret" "storage_conn" {
  name         = "storage-connection-string" # was STORAGE_CONNECTION_STRING
  value        = azurerm_storage_account.data.primary_connection_string
  key_vault_id = azurerm_key_vault.kv.id
  depends_on   = [azurerm_role_assignment.tf_kv_admin]
}

# --------- Chat (East US 2) ---------
resource "azurerm_key_vault_secret" "aoai_chat_endpoint" {
  name         = "azure-openai-chat-endpoint"
  value        = var.aoai_chat_endpoint
  key_vault_id = azurerm_key_vault.kv.id
  depends_on   = [azurerm_role_assignment.tf_kv_admin]
}

resource "azurerm_key_vault_secret" "aoai_chat_api_key" {
  name         = "azure-openai-chat-api-key"
  value        = var.aoai_chat_api_key
  key_vault_id = azurerm_key_vault.kv.id
  depends_on   = [azurerm_role_assignment.tf_kv_admin]
}

resource "azurerm_key_vault_secret" "aoai_chat_deployment" {
  name         = "azure-openai-chat-deployment"
  value        = var.aoai_chat_deployment
  key_vault_id = azurerm_key_vault.kv.id
  depends_on   = [azurerm_role_assignment.tf_kv_admin]
}

resource "azurerm_key_vault_secret" "aoai_chat_api_version" {
  name         = "azure-openai-chat-api-version"
  value        = var.aoai_chat_api_version
  key_vault_id = azurerm_key_vault.kv.id
  depends_on   = [azurerm_role_assignment.tf_kv_admin]
}

# --------- Embeddings (West Europe) ---------
# If you created this AOAI account with Terraform as azurerm_cognitive_account.aoai,
# we can pull endpoint/key directly from that resource:
resource "azurerm_key_vault_secret" "aoai_embeddings_endpoint" {
  name         = "azure-openai-embeddings-endpoint"
  value        = azurerm_cognitive_account.aoai.endpoint
  key_vault_id = azurerm_key_vault.kv.id
  depends_on   = [azurerm_role_assignment.tf_kv_admin]
}

resource "azurerm_key_vault_secret" "aoai_embeddings_api_key" {
  name         = "azure-openai-embeddings-api-key"
  value        = azurerm_cognitive_account.aoai.primary_access_key
  key_vault_id = azurerm_key_vault.kv.id
  depends_on   = [azurerm_role_assignment.tf_kv_admin]
}

resource "azurerm_key_vault_secret" "aoai_embeddings_deployment" {
  name         = "azure-openai-embeddings-deployment"
  value        = var.aoai_embeddings_deployment
  key_vault_id = azurerm_key_vault.kv.id
  depends_on   = [azurerm_role_assignment.tf_kv_admin]
}

resource "azurerm_key_vault_secret" "aoai_embeddings_api_version" {
  name         = "azure-openai-embeddings-api-version"
  value        = var.aoai_embeddings_api_version
  key_vault_id = azurerm_key_vault.kv.id
  depends_on   = [azurerm_role_assignment.tf_kv_admin]
}


output "key_vault_name" {
  value = azurerm_key_vault.kv.name
}

resource "azurerm_key_vault_secret" "qdrant_api_key" {
  name         = "qdrant-api-key"
  value        = var.qdrant_api_key
  key_vault_id = azurerm_key_vault.kv.id
  depends_on   = [azurerm_role_assignment.tf_kv_admin]
}
