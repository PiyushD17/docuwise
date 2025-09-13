locals {                                        # Local helper values (no inputs needed)
  location = "westeurope"                       # Azure region you want to use
  suffix   = substr(md5("docuwise-bootstrap"), # Deterministic 6-char suffix from an md5 hash
                    0, 6)                       # Keeps names short/unique where required
}
