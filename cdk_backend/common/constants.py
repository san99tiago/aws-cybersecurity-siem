# Constants used in the CDK constructs

# Constants for the Security Groups, ALB and ASG
APP_PORT = 443  # Some apps use 80, but Wazuh uses 443 for the dashaboard
ALB_PORT = 443  # Application Load Balancer port
INDEXER_PORT = 9200  # Wazuh Indexer port
MANAGER_PORT_1 = 1514  # Wazuh Manager port (remoted module for agents)
MANAGER_PORT_2 = 1515  # Wazuh Manager port (authd module for agents)
MANAGER_PORT_3 = 55000  # Wazuh Manager port (RESTful API module for agents)

# Constants for the ALB DNS in Route 53
DNS_SUBDOMAIN = "siem"  # For Example: siem.example.com
