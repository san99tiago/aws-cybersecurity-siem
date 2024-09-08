#!/bin/bash

####################################################################################################
# SCRIPT TO RUN IN THE DEMO SERVERS (THE ONES MONITORED BY WAZUH AGENTS)
####################################################################################################

# Enable extra logging
set -x

# Install amazon linux extras
sudo yum install -y amazon-linux-extras
sudo dnf update -y

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


# AGENT INSTALLATION LINUX (WAZUH)
echo "----- Preparing to install Wazuh Agent -----"

# Set the URL for the token and metadata services
TOKEN_URL="http://169.254.169.254/latest/api/token"
METADATA_URL="http://169.254.169.254/latest/meta-data"

# Get a token for the metadata service (valid for 21600 seconds, or 6 hours)
TOKEN=$(curl -s -X PUT "$TOKEN_URL" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

# Get the instance ID to have unique names for the agents in the SIEM dashboard
EC2_INSTANCE_ID=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" "$METADATA_URL/instance-id")

WAZUH_AGENT_NAME="workflow-server.${EC2_INSTANCE_ID}"
WAZUH_SIEM_ENDPOINT="siem.san99tiago.com"

echo "----- Installing Wazuh Agent -----"

curl -o wazuh-agent-4.8.2-1.x86_64.rpm https://packages.wazuh.com/4.x/yum/wazuh-agent-4.8.2-1.x86_64.rpm && sudo WAZUH_MANAGER="${WAZUH_SIEM_ENDPOINT}" WAZUH_AGENT_NAME="${WAZUH_AGENT_NAME}" rpm -ihv wazuh-agent-4.8.2-1.x86_64.rpm

sudo systemctl daemon-reload
sudo systemctl enable wazuh-agent
sudo systemctl start wazuh-agent
