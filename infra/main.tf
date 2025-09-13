resource "azurerm_resource_group" "rg" {
  name     = "rg-${local.name_prefix}" # rg-docuwise-dev
  location = var.location              # Region from input
  tags     = local.tags                # Apply tags
}

resource "azurerm_log_analytics_workspace" "law" {
  name                = "log-${local.name_prefix}"         # log-docuwise-dev
  location            = azurerm_resource_group.rg.location # Same region as RG
  resource_group_name = azurerm_resource_group.rg.name     # Put in the RG
  sku                 = "PerGB2018"                        # Standard, pay-per-GB
  retention_in_days   = 30                                 # Keep logs 30 days
  tags                = local.tags
}
