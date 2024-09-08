#!/bin/bash
####################################################################################################
# SCRIPT TO RUN IN THE MAIN WAZUH SIEM SERVER INSTANCE ON EC2 LAUNCH
####################################################################################################

# Enable extra logging
set -x

# Install amazon linux extras
sudo yum install -y amazon-linux-extras

# Refresh environment variables
source /etc/profile

# Update OS
echo "----- Updating OS -----"
sudo yum update -y

# Install and Initialize SSM Agent
# --> Note: hard-coded to us-east-1 region.. update to dynamic ref
echo "----- Initializing SSM Agent -----"
sudo yum install -y https://s3.us-east-1.amazonaws.com/amazon-ssm-us-east-1/latest/linux_amd64/amazon-ssm-agent.rpm
sudo systemctl enable amazon-ssm-agent
sudo systemctl start amazon-ssm-agent
