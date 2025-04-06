import logging
from ultralytics import YOLO
import zipfile
import boto3
import os
from sns import sns

class YOLOTrainer:
    def __init__(self, model_path, yaml_file, epochs, bucket_name):
        self.model_path = model_path
        self.yaml_file = yaml_file
        self.epochs = epochs
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3')
        self._configure_logging()
        self.sns_instance = sns() #these are at the default values, insert parameters to chagne, param1-arn, param2-message


    def _configure_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("train_yolo.log"),
                logging.StreamHandler()
            ]
        )

    def train_model(self, sns_topic_arn):
        try:
            if not os.path.exists(self.yaml_file):
                logging.error(f"YAML file '{self.yaml_file}' not found.")
                raise FileNotFoundError(f"YAML file '{self.yaml_file}' not found.")

            logging.info("Loading YOLO model...")
            model = YOLO(self.model_path)

            logging.info(f"Starting training for {self.epochs} epochs using data file '{self.yaml_file}'...")
            model.train(data=self.yaml_file, epochs=self.epochs)

            self.sns_instance.send_sns(topic_arn=sns_topic_arn, 
                                       message=f"Training completed for YOLO model.")
            logging.info("Training completed successfully.")

        except FileNotFoundError as e:
            logging.error(f"File error: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

    def zip_results(self, runs_dir='./runs', zip_path='./runs.zip'):
        with zipfile.ZipFile(zip_path, 'w') as zip:
            for path, directories, files in os.walk(runs_dir):
                for file in files:
                    file_name = os.path.join(path, file)
                    zip.write(file_name)

    def upload_results(self, zip_path, s3_key):
        self.s3_client.upload_file(zip_path, self.bucket_name, s3_key)

# Example usage
