terraform {                              # Terraform core settings for this project
  required_version = ">= 1.6.0"          # Require TF 1.6+ (works with 1.8 too)
  required_providers {                   # Declare providers this project uses
    azurerm = {                          # Azure Resource Manager provider (Azure)
      source  = "hashicorp/azurerm"      # Where to fetch the provider from
      version = "~> 3.100"               # Any 3.x >= 3.100, < 4.0
    }                                    # (No backend here -> local state on disk)
  }
}
