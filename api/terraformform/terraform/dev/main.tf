
provider "kubernetes" {
  config_context = "blackbox"
}

module "simple" {
  source   = "../modules/simple"
  env      = "dev"
  short_id = "nodb"
}


