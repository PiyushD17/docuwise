resource "azurerm_user_assigned_identity" "api_mi" {
  name                = "id-${local.name_prefix}-api" # MI for API container app
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  tags                = local.tags
}

resource "azurerm_user_assigned_identity" "worker_mi" {
  name                = "id-${local.name_prefix}-worker" # MI for Worker container app
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  tags                = local.tags
}

resource "azurerm_role_assignment" "api_blob_writer" {
  scope                = azurerm_storage_account.data.id                    # Grant at storage account scope
  role_definition_name = "Storage Blob Data Contributor"                    # Allows write to blobs
  principal_id         = azurerm_user_assigned_identity.api_mi.principal_id # Principal = API MI
}

resource "azurerm_role_assignment" "api_eh_sender" {
  scope                = azurerm_eventhub_namespace.ehns.id # Grant on EH namespace
  role_definition_name = "Azure Event Hubs Data Sender"     # Allows send
  principal_id         = azurerm_user_assigned_identity.api_mi.principal_id
}

resource "azurerm_role_assignment" "worker_eh_receiver" {
  scope                = azurerm_eventhub_namespace.ehns.id # Grant on EH namespace
  role_definition_name = "Azure Event Hubs Data Receiver"   # Allows listen
  principal_id         = azurerm_user_assigned_identity.worker_mi.principal_id
}
