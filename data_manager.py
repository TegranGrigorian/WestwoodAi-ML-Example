import zipfile
import boto3
import time

class S3DataHandler:
    def __init__(self, bucket_name, region_name=None):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3', region_name=region_name)

    def download_file(self, s3_key, local_path):
        # Download a file from S3
        self.s3_client.download_file(self.bucket_name, s3_key, local_path)

    def download_file_with_retry(self, s3_key, local_path, retries=3, delay=5):
        # Retry logic for downloading a file
        for attempt in range(retries):
            try:
                self.download_file(s3_key, local_path)
                return
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(delay)
                    continue
                raise e

    def validate_s3_key(self, s3_key):
        # Check if the S3 key exists
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except self.s3_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                raise FileNotFoundError(f"S3 key '{s3_key}' not found in bucket '{self.bucket_name}'.")
            else:
                raise

    def extract_zip(self, zip_path, extract_to='./'):
        # Extract a ZIP file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)

# Example usage
if __name__ == "__main__":
    bucket_name = 'train-object-detector-ec2-bucket'
    data_in_path = "in/roofsegment.zip"
    output_zip_file = 'data.zip'

    handler = S3DataHandler(bucket_name)
    if handler.validate_s3_key(data_in_path):
        handler.download_file_with_retry(data_in_path, output_zip_file)
        handler.extract_zip(output_zip_file)
