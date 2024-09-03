# External imports
from aws_cdk import (
    aws_certificatemanager,
    aws_ec2,
    aws_elasticloadbalancingv2 as aws_elbv2,
    aws_route53,
    aws_route53_targets,
    Duration,
    CfnOutput,
)
from constructs import Construct

# Own imports
from cdk_backend.common.constants import APP_PORT, ALB_PORT, DNS_SUBDOMAIN


class ALB(Construct):
    """
    Class to create the Application Load Balancer resources for the servers.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: aws_ec2.Vpc,
        short_name: str,
        security_group: aws_ec2.SecurityGroup,
        alb_target: aws_ec2.IInstance,
        hosted_zone_name: str,
    ) -> None:
        """
        :param scope (Construct): Parent of this stack, usually an 'App' or a 'Stage', but could be any construct.
        :param construct_id (str): The construct ID of this stack (same as aws-cdk Stack 'construct_id').
        :param vpc (aws_ec2.Vpc): The VPC where the Security Group will be created.
        :param short_name (str): The short name for the ALB resources.
        :param security_group (aws_ec2.SecurityGroup): The Security Group for the ALB.
        :param alb_target (aws_ec2.IInstance): The target for the ALB.
        :param hosted_zone_name (str): The hosted zone name for the ALB (e.g. example.com).
        """
        super().__init__(scope, construct_id)

        self.vpc = vpc
        self.short_name = short_name
        self.security_group = security_group
        self.alb_target = alb_target
        self.hosted_zone_name = hosted_zone_name

        # Main methods to create and configure the ALB
        self.create_alb()
        self.import_route_53_hosted_zone()
        self.configure_acm_certificate()
        self.configure_alb_listeners()
        self.configure_target_groups()
        self.configure_route_53_records()

    def create_alb(self):
        """
        Method to create the Application Load Balancer for the UI.
        """
        self.alb = aws_elbv2.ApplicationLoadBalancer(
            self,
            "LoadBalancer",
            vpc=self.vpc,
            internet_facing=True,
            load_balancer_name=self.short_name,
            security_group=self.security_group,
        )

    def import_route_53_hosted_zone(self):
        """
        Method to import the Route 53 hosted zone for the application.
        """
        # IMPORTANT: The hosted zone must be already created in Route 53!
        self.hosted_zone_name = self.hosted_zone_name
        self.domain_name = f"{DNS_SUBDOMAIN}.{self.hosted_zone_name}"
        self.hosted_zone = aws_route53.HostedZone.from_lookup(
            self,
            "HostedZone",
            domain_name=self.hosted_zone_name,
        )

    def configure_acm_certificate(self):
        """
        Method to configure the SSL certificate for the ALB.
        """
        self.certificate = aws_certificatemanager.Certificate(
            self,
            "Certificate",
            domain_name=self.domain_name,
            validation=aws_certificatemanager.CertificateValidation.from_dns(
                hosted_zone=self.hosted_zone,
            ),
        )

    def configure_alb_listeners(self):
        """
        Method to configure the ALB listeners for the UI.
        """
        self.https_listener = self.alb.add_listener(
            "ALB-HTTPS-Listener",
            open=True,
            port=ALB_PORT,
            protocol=aws_elbv2.ApplicationProtocol.HTTPS,
            certificates=[self.certificate],
        )

        # TODO: Add all the necessary listeners for the ALB
        # --> The ones needed for the Wazuh components

    def configure_target_groups(self):
        """
        Method to configure the target groups for the ALB.
        """
        self.https_listener_target_group = self.https_listener.add_targets(
            "ALB-HTTPS-TargetGroup",
            port=APP_PORT,  # Intentionally set to Application Port for the ASG
            protocol=aws_elbv2.ApplicationProtocol.HTTPS,  # Intentionally set to HTTPS for the ASG
            targets=[self.alb_target],
            health_check=aws_elbv2.HealthCheck(
                path="/",
                protocol=aws_elbv2.Protocol.HTTP,
                timeout=Duration.seconds(15),
                interval=Duration.minutes(5),
            ),
        )

    def configure_route_53_records(self):
        """
        Method to configure the Route 53 records for the ALB.
        """
        aws_route53.ARecord(
            self,
            "ALB-Record",
            zone=self.hosted_zone,
            target=aws_route53.RecordTarget.from_alias(
                aws_route53_targets.LoadBalancerTarget(self.alb)
            ),
            record_name=self.domain_name,
            comment=f"ALB DNS for {self.domain_name} for {self.short_name} application",
        )

        # Outputs for the custom domain and ALB DNS
        CfnOutput(
            self,
            "APP-DNS",
            value=f"https://{self.domain_name}",
            description="Application custom DNS",
        )
        CfnOutput(
            self,
            "ALB-DNS",
            value=f"https://{self.alb.load_balancer_dns_name}",
            description="ALB DNS",
        )
