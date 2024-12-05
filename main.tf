# i want to deploy an object database and a virtual machine instance and output the key and ip to connect
terraform {
  required_providers {
    huaweicloud = {
      source  = "huaweicloud/huaweicloud"
      version = ">= 1.0.0"
    }
  }
}

provider "huaweicloud" {
  region     = "ap-southeast-3"
  access_key = ""
  secret_key = ""
}

resource "huaweicloud_obs_bucket" "bucket" {
  bucket = "kuray-data"
}

resource "huaweicloud_compute_instance_v2" "vm_instance" {
  name              = "kuray-mono"
  flavor_id         = "s3.medium.2"
  image_id          = "1c136556-5a40-4382-884a-eb340532dc58"
  admin_pass        = "YourSecurePassword123!"
  availability_zone = "ap-southeast-3a"
  network {
    uuid = "d76cbec1-1289-4763-a09c-3cab6018ddd5"
  }
  user_data = <<-EOF
              #!/bin/bash
              echo "root:YourRootPassword123!" | chpasswd
              EOF
}


output "vm_ip" {
  value = huaweicloud_vpc_eip.eip.address
}

output "bucket_name" {
  value = huaweicloud_obs_bucket.bucket.bucket
}
