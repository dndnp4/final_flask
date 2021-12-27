import os
import boto3

from config import AWSConfig
from .encrypt import create_salt

default_dir = "./uploaded"

def s3_connection():
  # s3 = boto3.client('s3',
  #   aws_access_key_id = AWSConfig.AWS_ACCESS_KEY,
  #   aws_secret_access_key = AWSConfig.AWS_SECRET_KEY)
  s3 = boto3.client('s3')
  return s3

def get_temp_dir():
    is_dir = os.path.isdir(default_dir)
    if not is_dir:
        os.mkdir(default_dir)

    return os.path.abspath(default_dir)

def create_hashed_name(filename):
    temp = filename.split('.')
    ext = temp[-1]
    return {'name' : create_salt(20), 'ext' : ext }

def run(file):
    path = os.path.join(get_temp_dir(), file.filename)
    file.save(path)
    s3 = s3_connection()
    s3.upload_file(path, AWSConfig.ORIGIN_BUCKET_NAME, file.filename)
    os.remove(path)
