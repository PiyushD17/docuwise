resource "azurerm_resource_group" "tfstate" {  # Make a resource group to hold state storage
  name     = "rg-tfstate"                      # RG name
  location = local.location                    # Uses the region from locals
  tags     = { project = "docuwise", env = "dev" }  # Helpful metadata
}

resource "azurerm_storage_account" "tfstate" {       # Storage Account for Terraform state
  name                     = "tfst${local.suffix}"    # Must be 3–24 chars, lowercase, unique
  resource_group_name      = azurerm_resource_group.tfstate.name  # Put it in the RG above
  location                 = azurerm_resource_group.tfstate.location
  account_tier             = "Standard"               # Cheapest tier
  account_replication_type = "LRS"                    # Locally-redundant (cheap)
  min_tls_version          = "TLS1_2"                 # Security: TLS 1.2+
}

resource "azurerm_storage_container" "tfstate" {      # Blob container to hold the state file
  name                  = "tfstate"                   # Container name
  storage_account_name  = azurerm_storage_account.tfstate.name
  container_access_type = "private"                   # No anonymous access
}

output "tfstate_rg"        { value = azurerm_resource_group.tfstate.name }      # Print RG name
output "tfstate_account"   { value = azurerm_storage_account.tfstate.name }     # Print SA name
output "tfstate_container" { value = azurerm_storage_container.tfstate.name }   # Print container
output "tfstate_key"       { value = "docuwise/infra/terraform.tfstate" }       # Path/key to use
