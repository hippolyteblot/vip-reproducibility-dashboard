from vip_client.utils import vip
from utils.settings import API_KEY

vip.setApiKey('2lqr1b39050jdlld5ns489nnuu')


def download_file(wf_id, file_path):
    """Download the file from VIP"""
    print('Downloading file: ' + file_path)
    vip.download(file_path, 'tmp/vip_data/' + wf_id + '/' + file_path.split('/')[-1])