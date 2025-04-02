import unittest
from unittest.mock import patch, MagicMock
from data_manager import S3DataHandler
from train_yolo import YOLOTrainer
from sns import sns

class TestS3DataHandler(unittest.TestCase):
    @patch('boto3.client')
    def test_download_file(self, mock_boto_client):
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        handler = S3DataHandler(bucket_name="test-bucket")
        handler.download_file("test-key", "test-path")
        mock_s3.download_file.assert_called_once_with("test-bucket", "test-key", "test-path")

    @patch('boto3.client')
    def test_validate_s3_key(self, mock_boto_client):
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        handler = S3DataHandler(bucket_name="test-bucket")
        mock_s3.head_object.return_value = {}
        self.assertTrue(handler.validate_s3_key("test-key"))
        mock_s3.head_object.assert_called_once_with(Bucket="test-bucket", Key="test-key")

    @patch('zipfile.ZipFile')
    def test_extract_zip(self, mock_zipfile):
        handler = S3DataHandler(bucket_name="test-bucket")
        handler.extract_zip("test.zip", "./test-dir")
        mock_zipfile.assert_called_once_with("test.zip", 'r')
        mock_zipfile.return_value.extractall.assert_called_once_with("./test-dir")

class TestYOLOTrainer(unittest.TestCase):
    @patch('ultralytics.YOLO')
    @patch('boto3.client')
    def test_train_model(self, mock_boto_client, mock_yolo):
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model

        trainer = YOLOTrainer("test-model.pt", "test.yaml", 1, "test-bucket")
        with patch('os.path.exists', return_value=True):
            trainer.train_model()
        mock_yolo.assert_called_once_with("test-model.pt")
        mock_model.train.assert_called_once_with(data="test.yaml", epochs=1)

    @patch('zipfile.ZipFile')
    def test_zip_results(self, mock_zipfile):
        trainer = YOLOTrainer("test-model.pt", "test.yaml", 1, "test-bucket")
        trainer.zip_results(runs_dir="./runs", zip_path="./runs.zip")
        mock_zipfile.assert_called_once_with("./runs.zip", 'w')

    @patch('boto3.client')
    def test_upload_results(self, mock_boto_client):
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        trainer = YOLOTrainer("test-model.pt", "test.yaml", 1, "test-bucket")
        trainer.upload_results(zip_path="./runs.zip", s3_key="test-key")
        mock_s3.upload_file.assert_called_once_with("./runs.zip", "test-bucket", "test-key")

class TestSNS(unittest.TestCase):
    @patch('boto3.client')
    def test_send_sns(self, mock_boto_client):
        mock_sns = MagicMock()
        mock_boto_client.return_value = mock_sns
        sns_instance = sns()
        sns_instance.send_sns(topic_arn="test-arn", message="test-message")
        mock_sns.publish.assert_called_once_with(TopicArn="test-arn", Message="test-message")

if __name__ == "__main__":
    unittest.main()
