from WorkbookUnlocked import WorkbookUnlocked
from oyoms import DriveClient
from datetime import datetime, date, timedelta, timezone
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from tempfile import NamedTemporaryFile
from google.cloud import bigquery
from google.oauth2 import service_account
import os
import json
import io
import subprocess
import six
from bs4 import BeautifulSoup
import oyoms as om
import pytz
import base64
import calendar
from toolbox_auth import get_toolbox_cookies
import pandas as pd
import requests
from oyoms import TeamsClient

def install_package(package):
    subprocess.check_call(['pip', 'install', package])

# Since the server doesn't have matplotlib by default, hence this indirect way
package_name = 'matplotlib'
install_package(package_name)
import matplotlib.pyplot as plt

def render_mpl_table(data, col_widths=None, row_height=0.625, font_size=14,
                     header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                     bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        nrows, ncols = data.shape
        col_widths = col_widths or [3.0] * ncols  # Default width for each column
        # Calculate total width and height
        total_width = sum(col_widths)
        total_height = row_height * nrows
        fig, ax = plt.subplots(figsize=(total_width, total_height))
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, colWidths=col_widths, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in  six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    return ax

# Function to convert image to passable parameter during API call
def encode_file_to_base64_string(input_file):
    with open(input_file, "rb") as f:
        # Read the contents of the file
        data = f.read()
        # Encode the data to Base64
        encoded_data = base64.b64encode(data)
        # Decode bytes to string
        encoded_string = encoded_data.decode('utf-8')
    return encoded_string

# Microsoft Workbook Connection
def getMicrosoftAuthConfig(email_id, path='/prod-datapl-r-scheduler/team/ovh_chsh/sayak.adak1/data/sayak.adak1_ms.bin', container="prod-datapl-r-scheduler"):
    username = email_id.split('@')[0]
    blob_service_client = BlobServiceClient(account_url="https://zpdataplcodescheduler.blob.core.windows.net", credential= DefaultAzureCredential())
    container_client = blob_service_client.get_container_client(container)
    blob_client = container_client.get_blob_client(path)
    with NamedTemporaryFile(prefix=username+'_', delete=False) as temp_file:
        blob_data = blob_client.download_blob()
        temp_file.write(blob_data.readall())
    file_path = temp_file.name
    cache_name = file_path.split(username+'_')[-1]
    path='/'.join(file_path.split('/')[:-1])
    config = om.AuthConfig(email_id, style='local', path=path, cache_name=cache_name)
    return config

# Google BigQuery Connection
def getGoogleCredentials(email_id, path='/prod-datapl-r-scheduler/team/ovh_chsh/sayak.adak1/data/sayak_credentials.json', container="prod-datapl-r-scheduler"):
    username = email_id.split('@')[0]
    blob_service_client = BlobServiceClient(account_url="https://zpdataplcodescheduler.blob.core.windows.net", credential= DefaultAzureCredential())
    container_client = blob_service_client.get_container_client(container)
    blob_client = container_client.get_blob_client(path)
    with NamedTemporaryFile(prefix=username+'_', delete=False) as temp_file:
        blob_data = blob_client.download_blob()
        temp_file.write(blob_data.readall())
    file_path = temp_file.name
    print(blob_data)
    # Read the contents of the JSON file and print it in the log for debugginf purposes
    with open(file_path, 'r') as json_file:
        json_contents = json.load(json_file)
        # print(json.dumps(json_contents, indent=2))
    credentials = service_account.Credentials.from_service_account_file(file_path)
    print(credentials)
    return credentials

cookies = get_toolbox_cookies('kritig', 'Gratitude15#')
auth_config = getMicrosoftAuthConfig("sayak.adak1@oyorooms.com")
credentials = getGoogleCredentials("sayak.adak1@oyorooms.com")
client = bigquery.Client(credentials=credentials,project='leisure-bi')
