# Constants used in the CDK constructs

# Constants for the Security Groups, ALB and ASG
APP_PORT = 443  # Some apps use 80, but Wazuh uses 443
ALB_PORT = 443  # Application Load Balancer port


# Constants for the ALB DNS in Route 53
DNS_SUBDOMAIN = "siem"  # For Example: siem.example.com
