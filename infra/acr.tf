resource "azurerm_container_registry" "acr" {
  name                = "acr${local.suffix}" # e.g., "acra1b2c3" (must be lowercase, unique)
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic" # Cheapest SKU
  admin_enabled       = true    # Enable admin user (quick start)
  tags                = local.tags
}

output "acr_login_server" {
  value = azurerm_container_registry.acr.login_server
} # e.g., acra1b2c3.azurecr.io
output "acr_admin_user" {
  value = azurerm_container_registry.acr.admin_username
} # Admin username
output "acr_admin_pwd" {
  value     = azurerm_container_registry.acr.admin_password
  sensitive = true
} # Admin password
