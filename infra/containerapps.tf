resource "azurerm_container_app_environment" "cae" {
  name                       = "cae-${local.name_prefix}" # cae-docuwise-dev
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id # Attach to LAW for logs
  tags                       = local.tags
}
