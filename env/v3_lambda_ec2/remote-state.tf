terraform {
  backend "remote" {
    organization = "comic_crawler"

    workspaces {
      name = "v3-aws-deploy"
    }
  }
}
