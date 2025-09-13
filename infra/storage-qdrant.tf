# Azure Files (SMB) share for Qdrant data
resource "azurerm_storage_share" "qdrant" {
  name                 = "qdrant"
  storage_account_name = azurerm_storage_account.data.name
  quota                = 100 # GB; adjust later if needed
}

# Register the share with your Container Apps Environment
resource "azurerm_container_app_environment_storage" "qdrant" {
  name                         = "qdrantfiles"
  container_app_environment_id = azurerm_container_app_environment.cae.id
  account_name                 = azurerm_storage_account.data.name
  share_name                   = azurerm_storage_share.qdrant.name
  access_key                   = azurerm_storage_account.data.primary_access_key
  access_mode                  = "ReadWrite"
}
