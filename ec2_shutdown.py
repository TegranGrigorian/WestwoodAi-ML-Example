import os

class Ec2Shutdown:
    def __init__(self, instance_id):
        pass
    def shutdown(self):
        """
        This method will handle the logic to shutdown the EC2 instance.
        For example, it could use Boto3 to call the shutdown API for the given instance_id.
        """
        os.system('sudo shutdown -h now')
        pass