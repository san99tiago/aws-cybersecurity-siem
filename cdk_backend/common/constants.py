# Constants used in the CDK constructs

# Constants for the Security Groups, NLB and ASG
DASHBOARD_PORT = 443  # Wazuh Dashboard port
INDEXER_PORT = 9200  # Wazuh Indexer port
MANAGER_PORT_1 = 1514  # Wazuh Manager port (remoted module for agents)
MANAGER_PORT_2 = 1515  # Wazuh Manager port (authd module for agents)
MANAGER_PORT_3 = 55000  # Wazuh Manager port (RESTful API module for agents)

# Constants for the NLB DNS in Route 53
DNS_SUBDOMAIN = "siem"  # For Example: siem.example.com
