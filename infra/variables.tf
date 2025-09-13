variable "project" {
  type        = string
  description = "Short name, e.g. docuwise"
} # Input: project slug

variable "environment" {
  type        = string
  description = "dev/stage/prod"
} # Input: environment name

variable "location" {
  type        = string
  description = "Azure region"
  default     = "westeurope"
} # Input: region (default)

variable "tags" {
  type        = map(string)
  description = "Additional resource tags"
  default     = {}
} # Optional freeform tags

# -------- Chat (East US 2) --------
variable "aoai_chat_endpoint" {
  type        = string
  description = "Azure OpenAI Chat endpoint (https://<name>.openai.azure.com/)"
}

variable "aoai_chat_api_key" {
  type        = string
  description = "Azure OpenAI Chat API key"
  sensitive   = true
}

variable "aoai_chat_deployment" {
  type        = string
  description = "Azure OpenAI Chat deployment name (e.g., chat, docuwise-chat)"
  default     = "chat"
}

variable "aoai_chat_api_version" {
  type        = string
  description = "API version for Chat (preview if required by the model)"
  default     = "2024-12-01-preview"
}

# -------- Embeddings (West Europe) --------
# We only need the deployment name and API version as inputs.
# Endpoint & key come from the Terraform-managed AOAI cognitive account.
variable "aoai_embeddings_deployment" {
  type        = string
  description = "Embeddings deployment name (e.g., embeddings, docuwise-embeddings)"
  default     = "embeddings"
}

variable "aoai_embeddings_api_version" {
  type        = string
  description = "API version for Embeddings"
  default     = "2024-10-21"
}

variable "qdrant_api_key" {
  type        = string
  sensitive   = true
  description = "Static API key for Qdrant (used by QDRANT__SERVICE__API_KEY)."
}
