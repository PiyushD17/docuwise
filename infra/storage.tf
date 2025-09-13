resource "azurerm_storage_account" "data" {
  name                     = "st${local.suffix}" # e.g., "sta1b2c3" (lowercase)
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"

  blob_properties {
    delete_retention_policy { days = 7 } # Soft delete blobs for 7 days
  }

  tags = local.tags
}

resource "azurerm_storage_container" "uploads" {
  name                  = "uploads" # Container name your app will use
  storage_account_name  = azurerm_storage_account.data.name
  container_access_type = "private" # No public access
}

output "storage_account_name" {
  value = azurerm_storage_account.data.name
} # SA name
output "storage_uploads_container" {
  value = azurerm_storage_container.uploads.name
} # "uploads"
output "storage_primary_connection" {
  value     = azurerm_storage_account.data.primary_connection_string
  sensitive = true
} # Conn string
