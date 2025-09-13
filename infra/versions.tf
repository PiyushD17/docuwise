terraform {
  required_version = ">= 1.6.0" # Require TF 1.6+
  required_providers {
    azurerm = { # Use the AzureRM provider
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
  }
  backend "azurerm" {} # Tell TF to store state in Azure Blob (configured by backend.hcl)
}
