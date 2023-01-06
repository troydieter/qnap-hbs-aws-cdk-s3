from aws_cdk import Stack, RemovalPolicy, Tags, Duration, CfnOutput
from aws_cdk.aws_iam import User, AccessKey
from aws_cdk.aws_s3 import Bucket, BlockPublicAccess, BucketEncryption, LifecycleRule, \
    Transition, StorageClass
from aws_cdk.aws_secretsmanager import Secret
from constructs import Construct


class BackupStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, props, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        Tags.of(self).add("project", props["namespace"])
        namespace = props["namespace"]

        # S3 Backup Bucket
        backup_bucket = Bucket(self, "BackupBucket",
                               block_public_access=BlockPublicAccess.BLOCK_ALL,
                               encryption=BucketEncryption.S3_MANAGED,
                               enforce_ssl=True,
                               versioned=True,
                               removal_policy=RemovalPolicy.RETAIN,
                               bucket_name=props["namespace"],
                               lifecycle_rules=[LifecycleRule(transitions=[
                                   Transition(storage_class=StorageClass.INTELLIGENT_TIERING,
                                              transition_after=Duration.days(0))
                               ])]
                               )

        # IAM User
        backup_user = User(self, "BackupUser", user_name=f"{namespace}" + "_user")
        backup_bucket.grant_read_write(backup_user)

        # IAM Access Key and Secret Key
        access_key = AccessKey(self, "AccessKey", user=backup_user)
        secret_access_key = Secret(self, "Secret",
                                   description=f"{namespace}" + "_user_secretkey",
                                   removal_policy=RemovalPolicy.RETAIN,
                                   secret_string_value=access_key.secret_access_key
                                   )

        # Output
        CfnOutput(self, "BackupUserAccessKey", value=access_key.access_key_id,
                  description="The Backup user AWS IAM Access Key", export_name=f"{namespace}"
                                                                                + "-backup-user-access-key")
        CfnOutput(self, "BackupUserSecretAccessKey", value=secret_access_key.secret_arn,
                  description="Reference this ARN in AWS Secrets Manger to reveal the IAM Secret Access Key "
                              "for the Backup user", export_name=f"{namespace}"
                                                                 + "-backup-user-secret-access-key")
