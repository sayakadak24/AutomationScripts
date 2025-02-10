import requests
import pandas as pd
from pandas.io import gbq
import numpy as np
from datetime import datetime, date, timedelta, timezone
import json
import io
import subprocess
import six
from bs4 import BeautifulSoup
import pytz
import base64
from toolbox_auth import get_toolbox_cookies

# import matplotlib.pyplot as plt
def install_package(package):
    subprocess.check_call(['pip', 'install', package])

# Since the server doesn't have matplotlib by default, hence this indirect way
package_name = 'matplotlib'
install_package(package_name)
import matplotlib.pyplot as plt

utc_time = datetime.now(timezone.utc)

# Convert UTC time to IST
ist_timezone = pytz.timezone('Asia/Kolkata')  # Indian Standard Time
ist_time = utc_time.astimezone(ist_timezone)

# Print the converted time
print("Current system time in IST:", ist_time)
# Extracting current date and hour for caption during whapi calls
date = ist_time.strftime("%d-%m-%Y")
hour = ist_time.strftime("%H")
minute = ist_time.strftime("%M")


# DataFrame to Image
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


# Example usage:
# Specify custom column widths
# col_widths = [4.0, 3.5, 2.0, 2.0, 2.5, 2.0, 2.0, 2.0]  # Adjust widths as needed
# render_mpl_table(df, col_widths=col_widths, header_columns=0)
# plt.show()
# plt.savefig('Productivity.png')

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

cookies = get_toolbox_cookies('kritig', 'Gratitude15#')
print('hs_userid:', cookies['hs_userid'])
print('hs_ticket:', cookies['hs_ticket'])
print('PHPSESSID:', cookies['PHPSESSID'])
hs_userid = cookies['hs_userid']
hs_ticket = cookies['hs_ticket']
PHPSESSID = cookies['PHPSESSID']

# Navigating to the page where "Per agent (completed)" table is located
cookies = {
    'PHPSESSID': PHPSESSID,
    'hs_userid': hs_userid,
    'hs_ticket': hs_ticket,
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    # 'Cookie': 'PHPSESSID=p4v01b81ht0mmqkda9svug67m6; hs_userid=105470; hs_ticket=oSXDaaycNzMCz7FDOl36%2FaSYVm4KU1wzNkLNkcQ205kDnNTeAT99wh7M3c7h7rPva1z4iU8ZeaB6WCFByTjU9eIej5VRw8Ig%2BB38eOqnlA2sqsKecZgqoCHovOWstrygo5U5Wg%3D%3D',
    'Referer': 'https://toolbox.leisure-group.eu/email/?action=reporthe2022',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

params = {
    'action': 'reporthe2022',
    'subaction': 'go',
    'van_dag': ist_time.strftime("%d"),
    'van_maand': ist_time.strftime("%m"),
    'van_jaar': ist_time.strftime("%Y"),
    'tot_dag': ist_time.strftime("%d"),
    'tot_maand': ist_time.strftime("%m"),
    'tot_jaar': ist_time.strftime("%Y"),
}

response = requests.get('https://toolbox.leisure-group.eu/email/', params=params, cookies=cookies, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

# Extracting the table "Per agent (completed)" from the response page
tables = soup.find_all('table', class_='table table-condensed table-bordered table-striped')
# Extract table data
table = tables[1]
headers = [header.text.strip() for header in table.find_all('th')]
data = []
for row in table.find_all('tr'):
    row_data = [cell.text.strip() for cell in row.find_all('td')]
    if row_data:
        data.append(row_data)

# Create DataFrame
df_agent_completed = pd.DataFrame(data, columns=headers)
df_agent_completed = df_agent_completed.iloc[:, :-1]

# Saving the df_agent_completed as an image
# Specify custom column widths
# col_widths = [3.0, 3.0]  # Adjust widths as needed

# render_mpl_table(df_agent_completed, col_widths=col_widths, header_columns=0)
# plt.savefig('Per agent (completed).png')
# # Creating passable media/image parameter
# input_file = "Per agent (completed).png"  # Path to the input file
# base64_string = encode_file_to_base64_string(input_file)

# # Calling whapi to send the message to the group
key = 'hj9uTyE1Qh2gnet63FXzm3HjOO9PElLA'
# headers = {
#     'accept': 'application/json',
#     'authorization': 'Bearer ' + key,
#     'content-type': 'application/json',
# }

# json_data = {
#     'to': '917406809635-1623399518@g.us',
#     'media': 'data:image/png;name=completed.png;base64,' + base64_string,
#     'caption': date + ' ' + hour + 'PM Productivity update: Contact HO', 
# }

# response = requests.post('https://gate.whapi.cloud/messages/image', headers=headers, json=json_data)
# if response.status_code == 200:
#     print("Image sent successfully.")
# else:
#     print("Image sending failed. Status code:", response.status_code)

# import requests

# cookies = {
#     'PHPSESSID': PHPSESSID,
#     'hs_userid': hs_userid,
#     'hs_ticket': hs_ticket,
# }

# headers = {
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
#     'Accept-Language': 'en-US,en;q=0.9',
#     'Connection': 'keep-alive',
#     # 'Cookie': 'PHPSESSID=6gd8epg619ph0go1stg6aqsdg4; hs_userid=105470; hs_ticket=RddYdMujqARktDKr5ZCdt1qSG%2BinqOiygz68ce4rw%2BCMX5ubS7silo2sYRd4n4%2BDUE1A23lAObOyG00osg8rOuWoEAJ%2B4wCx8yaKfnDS8JBGhQCUKOEqT4Wgihj6WO39eZmzeg%3D%3D',
#     'Referer': 'https://toolbox.leisure-group.eu/email/?action=search&direct=1',
#     'Sec-Fetch-Dest': 'document',
#     'Sec-Fetch-Mode': 'navigate',
#     'Sec-Fetch-Site': 'same-origin',
#     'Sec-Fetch-User': '?1',
#     'Upgrade-Insecure-Requests': '1',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
#     'sec-ch-ua': '"Chromium";v="124", "Microsoft Edge";v="124", "Not-A.Brand";v="99"',
#     'sec-ch-ua-mobile': '?0',
#     'sec-ch-ua-platform': '"Windows"',
# }

# params = {
#     'action': 'setafd',
#     'curr': 'L2VtYWlsLz9hY3Rpb249c2VhcmNoJmRpcmVjdD0x',
#     'nafd': '2',
# }

# response = requests.get('https://toolbox.leisure-group.eu/', params=params, cookies=cookies, headers=headers)

# # Naviagting to the page to extract "Agent Productivity" table
# cookies = {
#     'PHPSESSID': PHPSESSID,
#     'hs_userid': hs_userid,
#     'hs_ticket': hs_ticket,
# }

# headers = {
#     'Accept': 'text/javascript, text/html, application/xml, text/xml, /',
#     'Accept-Language': 'en-US,en;q=0.9',
#     'Connection': 'keep-alive',
#     # 'Content-Length': '0',
#     'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
#     # 'Cookie': 'PHPSESSID=p4v01b81ht0mmqkda9svug67m6; hs_userid=105470; hs_ticket=oSXDaaycNzMCz7FDOl36%2FaSYVm4KU1wzNkLNkcQ205kDnNTeAT99wh7M3c7h7rPva1z4iU8ZeaB6WCFByTjU9eIej5VRw8Ig%2BB38eOqnlA2sqsKecZgqoCHovOWstrygo5U5Wg%3D%3D',
#     'Origin': 'https://toolbox.leisure-group.eu',
#     'Referer': 'https://toolbox.leisure-group.eu/email/?action=search&direct=1',
#     'Sec-Fetch-Dest': 'empty',
#     'Sec-Fetch-Mode': 'cors',
#     'Sec-Fetch-Site': 'same-origin',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
#     'X-Prototype-Version': '1.7.1',
#     'X-Requested-With': 'XMLHttpRequest',
#     'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
#     'sec-ch-ua-mobile': '?0',
#     'sec-ch-ua-platform': '"Windows"',
# }

# params = {
#     'action': 'ajax',
#     'subaction': 'monitor',
#     'short': '1',
# }

# response = requests.post('https://toolbox.leisure-group.eu/email/', params=params, cookies=cookies, headers=headers)
# soup = BeautifulSoup(response.content, "html.parser")
import requests
from bs4 import BeautifulSoup
from IPython.display import display_html

# Define the cookies and headers
# cookies = {
#     'hs_userid': '105470',
#     'hs_ticket': 'RddYdMujqARktDKr5ZCdt1qSG%2BinqOiygz68ce4rw%2BCMX5ubS7silo2sYRd4n4%2BDUE1A23lAObOyG00osg8rOuWoEAJ%2B4wCx8yaKfnDS8JBGhQCUKOEqT4Wgihj6WO39eZmzeg%3D%3D',
#     'PHPSESSID': 'bc8imdkiq7rm391d2lkpkmqgr7',
# }

cookies = {
    'PHPSESSID': PHPSESSID,
    'hs_userid': hs_userid,
    'hs_ticket': hs_ticket,
}

headers_initial = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Referer': 'https://toolbox.leisure-group.eu/email/?action=search&direct=1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
    'sec-ch-ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

params_initial = {
    'action': 'setafd',
    'curr': 'L2VtYWlsLz9hY3Rpb249c2VhcmNoJmRpcmVjdD0x',
    'nafd': '2',
}

# Make the initial GET request
response = requests.get('https://toolbox.leisure-group.eu/', params=params_initial, cookies=cookies, headers=headers_initial, allow_redirects=False)

# Check if the response indicates a redirect
if response.status_code in [301, 302]:
    # Get the redirection URL from the 'Location' header
    redirect_url = response.headers.get('Location')

    if redirect_url:
        # Construct the full URL for the redirection
        full_redirect_url = requests.compat.urljoin('https://toolbox.leisure-group.eu', redirect_url)

        # Make the second GET request to the redirected URL
        final_response = requests.get(full_redirect_url, cookies=cookies, headers=headers_initial)

        # Check if the second request is successful
        if final_response.status_code == 200:
            # Parse the content of the final response
            soup = BeautifulSoup(final_response.content, "html.parser")
            # display_html(str(soup), raw=True)

            # Prepare for the third request
            headers_third = {
                'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
                'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://toolbox.leisure-group.eu',
                'Referer': 'https://toolbox.leisure-group.eu/email/?action=search&direct=1',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
                'X-Prototype-Version': '1.7.1',
                'X-Requested-With': 'XMLHttpRequest',
                'sec-ch-ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }

            params_third = {
                'action': 'ajax',
                'subaction': 'monitor',
                'short': '1',
            }

            # Make the third POST request
            third_response = requests.post('https://toolbox.leisure-group.eu/email/', params=params_third, cookies=cookies, headers=headers_third)

            # Check the third response and parse it
            if third_response.status_code == 200:
                soup_third = BeautifulSoup(third_response.content, "html.parser")
                # display_html(str(soup_third), raw=True)
            else:
                print(f"Third request resulted in status code: {third_response.status_code}")
        else:
            print(f"Second request resulted in status code: {final_response.status_code}")
    else:
        print("No redirection URL found.")
else:
    print("Initial request did not result in a redirect.")
    soup = BeautifulSoup(response.content, "html.parser")
    # display_html(str(soup), raw=True)

# Extracting the desired table
# Find all tables with class 'repline'
tables = soup_third.find_all('table', class_='repline')

def convert_to_numeric(value):
    if pd.isnull(value):
        return 0
    try:
        return int(float(value))
    except ValueError:
        try:
            return int(float(value))
        except ValueError:
            return 0

# Extract header from the 21st table
# header_row = tables[22].find('tr', class_='replinedown')
# headers = [header.text.strip() for header in header_row.find_all('div')]

# # Initialize an empty list to store the data
# data = []

# # Iterate through tables starting from index 21
# for table in tables[23:]:
#     rows = table.find_all('tr', class_='replinedown')
#     for row in rows:
#         # Extract row data
#         row_data = [cell.text.strip() for cell in row.find_all('div')]
#         # Append row data to the list
#         data.append(row_data)

# tables = soup.find_all('table', class_='repline')

def convert_to_numeric(value):
    if pd.isnull(value):
        return 0
    try:
        return int(float(value))
    except ValueError:
        try:
            return int(float(value))
        except ValueError:
            return 0

# Define the keywords to search for
keywords = ["Agent", "Time", "Answered", "Forwarded", "Delegated ext", "Delegated int", "Ignored", "Outbound"]

# Initialize variables to store the target table and index
target_table = None
target_index = -1

# Search for the table containing the desired keywords
for index, table in enumerate(tables):
    # Get all rows in the table
    rows = table.find_all('tr')
    for row in rows:
        # Check if any keyword is found in the row
        row_text = row.get_text(separator=' ').strip()  # Get the row text
        if any(keyword in row_text for keyword in keywords):
            target_table = table
            target_index = index
            break
    if target_table:  # Break outer loop if target table is found
        break

data = []
# Check if a table was found
if target_table:
    print(f"Target table found at index {target_index}")
    # Extract header from the 21st table
    header_row = tables[target_index].find('tr', class_='replinedown')
    headers = [header.text.strip() for header in header_row.find_all('div')]
    
    # Initialize an empty list to store the data
    
    # Iterate through tables starting from index 21
    for table in tables[target_index+1:]:
        rows = table.find_all('tr', class_='replinedown')
        for row in rows:
            # Extract row data
            row_data = [cell.text.strip() for cell in row.find_all('div')]
            # Append row data to the list
            data.append(row_data)
        
    # # Extract headers
    # header_row = target_table.find('tr', class_='replinedown')
    # headers = [header.text.strip() for header in header_row.find_all('div')]
    
    # # Extract data rows
    # data = []
    # data_rows = target_table.find_all('tr', class_='replinedown')
    # for row in data_rows:
    #     row_data = [cell.text.strip() for cell in row.find_all('div')]
    #     data.append(row_data)
    
    # Create a DataFrame
    df = pd.DataFrame(data, columns=headers)
    print(df)
else:
    print("Target table not found.")


# Get user ids of agents
# Initialize an empty list to store user data
# user_data = []

# # Iterate through tables starting from index 21
# for table in tables[21:]:
#     rows = table.find_all('tr', class_='replinedown')
#     for row in rows:
#         # Extract user id and username
#         user_id = row.find('a')['href'].split('=')[-1]
#         username = row.find('a').text.strip()
#         # Append user data to the list
#         user_data.append({'user_id': user_id, 'username': username})

# Display user data
# for user in user_data:
#     print(user)

# userID = pd.DataFrame(user_data)

def get_email_counts(user_id):
    cookies = {
        'PHPSESSID': PHPSESSID,
        'hs_userid': hs_userid,
        'hs_ticket': hs_ticket,
    }
    
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        # 'Cookie': 'PHPSESSID=6gd8epg619ph0go1stg6aqsdg4; hs_userid=105470; hs_ticket=RddYdMujqARktDKr5ZCdt1qSG%2BinqOiygz68ce4rw%2BCMX5ubS7silo2sYRd4n4%2BDUE1A23lAObOyG00osg8rOuWoEAJ%2B4wCx8yaKfnDS8JBGhQCUKOEqT4Wgihj6WO39eZmzeg%3D%3D',
        'Referer': 'https://toolbox.leisure-group.eu/email/?action=search&direct=1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
        'sec-ch-ua': '"Chromium";v="124", "Microsoft Edge";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    
    params = {
        'action': 'agentsentmail',
        'subaction': 'go',
        'van_dag': ist_time.strftime("%d"),
        'van_maand': ist_time.strftime("%m"),
        'van_jaar': ist_time.strftime("%Y"),
        'tot_dag': ist_time.strftime("%d"),
        'tot_maand': ist_time.strftime("%m"),
        'tot_jaar': ist_time.strftime("%Y"),
        'selected_user': user_id,
    }
    
    response = requests.get('https://toolbox.leisure-group.eu/email/', params=params, cookies=cookies, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # from IPython.display import display_html
    # display_html(str(soup), raw=True)
    
    # Find the table
    table = soup.find('table', class_='table')

    # If no table is found, return counts as zero
    if not table:
        return {'L1': 0, 'L2': 0, 'L3': 0, 'AM': 0, 'Others': 0}

    # Initialize counters for each category
    counts = {'L1': 0, 'L2': 0, 'L3': 0, 'AM': 0, 'Others': 0}
    
    # Find all rows in the table except the header row
    rows = table.find_all('tr')[1:]
    
    # Iterate over each row
    for row in rows:
        # Find all cells in the row
        cells = row.find_all('td')
        # Extract Label1 and Label2 values from respective cells
        label1 = cells[-2].text.strip()
        label2 = cells[-1].text.strip()
        dept = cells[-7].text.strip()
        # Determine the category and update counts
        if dept == 'OST AM':
            counts['AM'] += 1        
        elif label1 == 'L1' or label2 == 'L1':
            counts['L1'] += 1
        elif label1 == 'L2' or label2 == 'L2':
            counts['L2'] += 1
        elif label1 == 'L3' or label2 == 'L3':
            counts['L3'] += 1
        else:
            counts['Others'] += 1
    return counts

# userID['L1'] = userID['user_id'].apply(lambda user_id: get_email_counts(user_id)['L1'])
# userID['L2'] = userID['user_id'].apply(lambda user_id: get_email_counts(user_id)['L2'])
# userID['L3'] = userID['user_id'].apply(lambda user_id: get_email_counts(user_id)['L3'])
# userID['AM'] = userID['user_id'].apply(lambda user_id: get_email_counts(user_id)['AM'])
# userID['Others'] = userID['user_id'].apply(lambda user_id: get_email_counts(user_id)['Others'])

# userID['Total'] = userID[['L1', 'L2', 'L3', 'AM', 'Others']].sum(axis=1)
# userID.drop('user_id', axis=1, inplace=True)
# userID.rename(columns={'username': 'Agent'}, inplace=True)

# Create DataFrame
df_agent = pd.DataFrame(data, columns=headers)
print(df_agent.columns)
# Convert string values to numeric in specified columns
df_agent['Answered'] = df_agent['Answered'].apply(convert_to_numeric)
df_agent['Forwarded'] = df_agent['Forwarded'].apply(convert_to_numeric)
df_agent['Delegated ext'] = df_agent['Delegated ext'].apply(convert_to_numeric)
df_agent['Delegated int'] = df_agent['Delegated int'].apply(convert_to_numeric)
df_agent['Ignored'] = df_agent['Ignored'].apply(convert_to_numeric)
df_agent['Outbound'] = df_agent['Outbound'].apply(convert_to_numeric)

df_agent = pd.merge(df_agent, df_agent_completed, on='Agent', how='left')
df_agent.rename(columns={'completed': 'Contact HO'}, inplace=True)
# df_agent = df_agent.fillna(value="")
df_agent['Contact HO'] = df_agent['Contact HO'].apply(convert_to_numeric)
# Summing up the columns
df_agent['Total'] = df_agent[['Answered', 'Forwarded', 'Delegated ext', 'Delegated int', 'Outbound', 'Contact HO']].sum(axis=1)
print(df_agent.columns)
# Replace 0 with empty strings
df_agent.replace(0, '', inplace=True)

# Converting the dataframe to image
# Specify custom column widths
df_agent = df_agent.fillna(value="")
agent_names_ind = ["Kavita Fernande","Ritika Koul","rishabhj","karank","Aayushmaan Gehlote","mallikasantani","ashish pandey","Divesh Kaushik", "Lakshya Thapa","Sagar Sharma","Tanisk Thakur","Raghav Sharma","Raj Bishwakarma","Umed Singh","Deepak Shukla","Amit Sharma", "Nikita Gurung", "Raman- kohli", "Kartik Bangard", "Renu shahi", "Sachin chourasia","Nikita Gurung","Amit Sharma","Raman- kohli","Renu Shahi","Umed Singh","Deepak Shukla","Raj Bishwakarma","Tanisk Thakur","Raghav Sharma","Lakshya Thapa","Divesh Kaushik","Chirag Saini","Sai Prashad","Manish Matela","Rajat Sharma","vaishali- khatwani","stuti singh"]
df_agent_ind = df_agent[df_agent['Agent'].isin(agent_names_ind)]
# List of agent names to filter
agent_names_L3 = ["Amit Sharma", "Nikita Gurung", "Raman- kohli", "Kartik Bangard", "Vineet Kumar", "Renu shahi", "Sachin chourasia"]

# Filter DataFrame to include only rows with the specified agent names
df_agent_L3 = df_agent[df_agent['Agent'].isin(agent_names_L3)]

# Reset index if needed
df_agent_L3.reset_index(drop=True, inplace=True)


# Converting the dataframe to image
# Specify custom column widths
col_widths = [4.0, 3.5, 2.0, 2.0, 2.5, 2.0, 2.0, 2.0, 2.0, 1.5]  # Adjust widths as needed

render_mpl_table(df_agent_ind, col_widths=col_widths, header_columns=0)
# plt.show()
plt.savefig('Productivity.png')

render_mpl_table(df_agent_L3, col_widths=col_widths, header_columns=0)
# plt.show()
plt.savefig('L3_Productivity.png')

# col_widths = [4.0, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5]  # Adjust widths as needed
# render_mpl_table(userID, col_widths=col_widths, header_columns=0)
# # plt.show()
# plt.savefig('L123.png')
input_file = "Productivity.png"  # Path to the input file
base64_string = encode_file_to_base64_string(input_file)

headers = {
    'accept': 'application/json',
    'authorization': 'Bearer ' + key,
    'content-type': 'application/json',
}

# json_data = {
#     'to': '917406809635-1623399518@g.us',
#     'media': 'data:image/png;name=Productivity.png;base64,' + base64_string,
#     'caption': date + ' ' + hour + 'PM Productivity update',
# }

json_data = {
    'to': '120363315815923835@g.us',
    'media': 'data:image/png;name=Productivity.png;base64,' + base64_string,
    'caption': date + ' ' + hour + minute + 'hrs Productivity update',
}

response = requests.post('https://gate.whapi.cloud/messages/image', headers=headers, json=json_data)

# input_file = "L123.png"  # Path to the input file
# base64_string = encode_file_to_base64_string(input_file)
## CC
cookies = {
    'PHPSESSID': PHPSESSID,
    'hs_userid': hs_userid,
    'hs_ticket': hs_ticket,
}

headers_initial = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Referer': 'https://toolbox.leisure-group.eu/email/?action=search&direct=1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
    'sec-ch-ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

params_initial = {
    'action': 'setafd',
    'curr': 'L2VtYWlsLz9hY3Rpb249c2VhcmNoJmRpcmVjdD0x',
    'nafd': '50',
}

# Make the initial GET request
response = requests.get('https://toolbox.leisure-group.eu/', params=params_initial, cookies=cookies, headers=headers_initial, allow_redirects=False)

# Check if the response indicates a redirect
if response.status_code in [301, 302]:
    # Get the redirection URL from the 'Location' header
    redirect_url = response.headers.get('Location')

    if redirect_url:
        # Construct the full URL for the redirection
        full_redirect_url = requests.compat.urljoin('https://toolbox.leisure-group.eu', redirect_url)

        # Make the second GET request to the redirected URL
        final_response = requests.get(full_redirect_url, cookies=cookies, headers=headers_initial)

        # Check if the second request is successful
        if final_response.status_code == 200:
            # Parse the content of the final response
            soup = BeautifulSoup(final_response.content, "html.parser")
            # display_html(str(soup), raw=True)

            # Prepare for the third request
            headers_third = {
                'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
                'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://toolbox.leisure-group.eu',
                'Referer': 'https://toolbox.leisure-group.eu/email/?action=search&direct=1',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
                'X-Prototype-Version': '1.7.1',
                'X-Requested-With': 'XMLHttpRequest',
                'sec-ch-ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }

            params_third = {
                'action': 'ajax',
                'subaction': 'monitor',
                'short': '1',
            }

            # Make the third POST request
            third_response = requests.post('https://toolbox.leisure-group.eu/email/', params=params_third, cookies=cookies, headers=headers_third)

            # Check the third response and parse it
            if third_response.status_code == 200:
                soup_third = BeautifulSoup(third_response.content, "html.parser")
                # display_html(str(soup_third), raw=True)
            else:
                print(f"Third request resulted in status code: {third_response.status_code}")
        else:
            print(f"Second request resulted in status code: {final_response.status_code}")
    else:
        print("No redirection URL found.")
else:
    print("Initial request did not result in a redirect.")
    soup = BeautifulSoup(response.content, "html.parser")
    # display_html(str(soup), raw=True)

# Extracting the desired table
# Find all tables with class 'repline'
# tables = soup_third.find_all('table', class_='repline')

# def convert_to_numeric(value):
#     if pd.isnull(value):
#         return 0
#     try:
#         return int(float(value))
#     except ValueError:
#         try:
#             return int(float(value))
#         except ValueError:
#             return 0

# # Extract header from the 21st table
# header_row = tables[41].find('tr', class_='replinedown')
# headers = [header.text.strip() for header in header_row.find_all('div')]

# # Initialize an empty list to store the data
# data = []

# # Iterate through tables starting from index 21
# for table in tables[42:]:
#     rows = table.find_all('tr', class_='replinedown')
#     for row in rows:
#         # Extract row data
#         row_data = [cell.text.strip() for cell in row.find_all('div')]
#         # Append row data to the list
#         data.append(row_data)
        
tables = soup_third.find_all('table', class_='repline')

def convert_to_numeric(value):
    if pd.isnull(value):
        return 0
    try:
        return int(float(value))
    except ValueError:
        try:
            return int(float(value))
        except ValueError:
            return 0

# Define the keywords to search for
keywords = ["Agent", "Time", "Answered", "Forwarded", "Delegated ext", "Delegated int", "Ignored", "Outbound"]

# Initialize variables to store the target table and index
target_table = None
target_index = -1

# Search for the table containing the desired keywords
for index, table in enumerate(tables):
    # Get all rows in the table
    rows = table.find_all('tr')
    for row in rows:
        # Check if any keyword is found in the row
        row_text = row.get_text(separator=' ').strip()  # Get the row text
        if any(keyword in row_text for keyword in keywords):
            target_table = table
            target_index = index
            break
    if target_table:  # Break outer loop if target table is found
        break

data = []
# Check if a table was found
if target_table:
    print(f"Target table found at index {target_index}")
    # Extract header from the 21st table
    header_row = tables[target_index].find('tr', class_='replinedown')
    headers = [header.text.strip() for header in header_row.find_all('div')]
    
    # Initialize an empty list to store the data
    
    # Iterate through tables starting from index 21
    for table in tables[target_index+1:]:
        rows = table.find_all('tr', class_='replinedown')
        for row in rows:
            # Extract row data
            row_data = [cell.text.strip() for cell in row.find_all('div')]
            # Append row data to the list
            data.append(row_data)
        
    # # Extract headers
    # header_row = target_table.find('tr', class_='replinedown')
    # headers = [header.text.strip() for header in header_row.find_all('div')]
    
    # # Extract data rows
    # data = []
    # data_rows = target_table.find_all('tr', class_='replinedown')
    # for row in data_rows:
    #     row_data = [cell.text.strip() for cell in row.find_all('div')]
    #     data.append(row_data)
    
    # Create a DataFrame
    df = pd.DataFrame(data, columns=headers)
    print(df)
else:
    print("Target table not found.")



# Create DataFrame
df_agent = pd.DataFrame(data, columns=headers)
print(df_agent.columns)
# Convert string values to numeric in specified columns
df_agent['Answered'] = df_agent['Answered'].apply(convert_to_numeric)
df_agent['Forwarded'] = df_agent['Forwarded'].apply(convert_to_numeric)
df_agent['Delegated ext'] = df_agent['Delegated ext'].apply(convert_to_numeric)
df_agent['Delegated int'] = df_agent['Delegated int'].apply(convert_to_numeric)
df_agent['Ignored'] = df_agent['Ignored'].apply(convert_to_numeric)
df_agent['Outbound'] = df_agent['Outbound'].apply(convert_to_numeric)

df_agent.rename(columns={'completed': 'Contact HO'}, inplace=True)
# df_agent = df_agent.fillna(value="")
# Summing up the columns
df_agent['Total'] = df_agent[['Answered', 'Forwarded', 'Delegated ext', 'Delegated int', 'Outbound','Ignored']].sum(axis=1)
print(df_agent.columns)
# Replace 0 with empty strings
df_agent.replace(0, '', inplace=True)

# Converting the dataframe to image
# Specify custom column widths
df_agent = df_agent.fillna(value="")
# Specify custom column widths
col_widths = [4.0, 3.5, 2.0, 2.0, 2.5, 2.0, 2.0, 2.0, 2.0, 1.5]  # Adjust widths as needed

render_mpl_table(df_agent, col_widths=col_widths, header_columns=0)
plt.show()
plt.savefig('Productivity1.png')

#HS
import requests
from bs4 import BeautifulSoup
from IPython.display import display_html

# Define the cookies and headers
# cookies = {
#     'hs_userid': '105470',
#     'hs_ticket': 'RddYdMujqARktDKr5ZCdt1qSG%2BinqOiygz68ce4rw%2BCMX5ubS7silo2sYRd4n4%2BDUE1A23lAObOyG00osg8rOuWoEAJ%2B4wCx8yaKfnDS8JBGhQCUKOEqT4Wgihj6WO39eZmzeg%3D%3D',
#     'PHPSESSID': 'bc8imdkiq7rm391d2lkpkmqgr7',
# }

cookies = {
    'PHPSESSID': PHPSESSID,
    'hs_userid': hs_userid,
    'hs_ticket': hs_ticket,
}

headers_initial = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Referer': 'https://toolbox.leisure-group.eu/email/?action=search&direct=1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
    'sec-ch-ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

params_initial = {
    'action': 'setafd',
    'curr': 'L2VtYWlsLz9hY3Rpb249c2VhcmNoJmRpcmVjdD0x',
    'nafd': '2',
}

# Make the initial GET request
response = requests.get('https://toolbox.leisure-group.eu/', params=params_initial, cookies=cookies, headers=headers_initial, allow_redirects=False)

# Check if the response indicates a redirect
if response.status_code in [301, 302]:
    # Get the redirection URL from the 'Location' header
    redirect_url = response.headers.get('Location')

    if redirect_url:
        # Construct the full URL for the redirection
        full_redirect_url = requests.compat.urljoin('https://toolbox.leisure-group.eu', redirect_url)

        # Make the second GET request to the redirected URL
        final_response = requests.get(full_redirect_url, cookies=cookies, headers=headers_initial)

        # Check if the second request is successful
        if final_response.status_code == 200:
            # Parse the content of the final response
            soup = BeautifulSoup(final_response.content, "html.parser")
            # display_html(str(soup), raw=True)

            # Prepare for the third request
            headers_third = {
                'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
                'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://toolbox.leisure-group.eu',
                'Referer': 'https://toolbox.leisure-group.eu/email/?action=search&direct=1',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
                'X-Prototype-Version': '1.7.1',
                'X-Requested-With': 'XMLHttpRequest',
                'sec-ch-ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }

            params_third = {
                'action': 'ajax',
                'subaction': 'monitor',
                'short': '1',
            }

            # Make the third POST request
            third_response = requests.post('https://toolbox.leisure-group.eu/email/', params=params_third, cookies=cookies, headers=headers_third)

            # Check the third response and parse it
            if third_response.status_code == 200:
                soup_third = BeautifulSoup(third_response.content, "html.parser")
                # display_html(str(soup_third), raw=True)
            else:
                print(f"Third request resulted in status code: {third_response.status_code}")
        else:
            print(f"Second request resulted in status code: {final_response.status_code}")
    else:
        print("No redirection URL found.")
else:
    print("Initial request did not result in a redirect.")
    soup = BeautifulSoup(response.content, "html.parser")
    # display_html(str(soup), raw=True)

# Extracting the desired table
# Find all tables with class 'repline'
tables = soup_third.find_all('table', class_='repline')
# tables = soup.find_all('table', class_='repline')

def convert_to_numeric(value):
    if pd.isnull(value):
        return 0
    try:
        return int(float(value))
    except ValueError:
        try:
            return int(float(value))
        except ValueError:
            return 0

# Define the keywords to search for
keywords = ["Agent", "Time", "Answered", "Forwarded", "Delegated ext", "Delegated int", "Ignored", "Outbound"]

# Initialize variables to store the target table and index
target_table = None
target_index = -1

# Search for the table containing the desired keywords
for index, table in enumerate(tables):
    # Get all rows in the table
    rows = table.find_all('tr')
    for row in rows:
        # Check if any keyword is found in the row
        row_text = row.get_text(separator=' ').strip()  # Get the row text
        if any(keyword in row_text for keyword in keywords):
            target_table = table
            target_index = index
            break
    if target_table:  # Break outer loop if target table is found
        break

data = []
# Check if a table was found
if target_table:
    print(f"Target table found at index {target_index}")
    # Extract header from the 21st table
    header_row = tables[target_index].find('tr', class_='replinedown')
    headers = [header.text.strip() for header in header_row.find_all('div')]
    
    # Initialize an empty list to store the data
    
    # Iterate through tables starting from index 21
    for table in tables[target_index+1:]:
        rows = table.find_all('tr', class_='replinedown')
        for row in rows:
            # Extract row data
            row_data = [cell.text.strip() for cell in row.find_all('div')]
            # Append row data to the list
            data.append(row_data)
        
    # # Extract headers
    # header_row = target_table.find('tr', class_='replinedown')
    # headers = [header.text.strip() for header in header_row.find_all('div')]
    
    # # Extract data rows
    # data = []
    # data_rows = target_table.find_all('tr', class_='replinedown')
    # for row in data_rows:
    #     row_data = [cell.text.strip() for cell in row.find_all('div')]
    #     data.append(row_data)
    
    # Create a DataFrame
    df = pd.DataFrame(data, columns=headers)
    print(df)
else:
    print("Target table not found.")
# def convert_to_numeric(value):
#     if pd.isnull(value):
#         return 0
#     try:
#         return int(float(value))
#     except ValueError:
#         try:
#             return int(float(value))
#         except ValueError:
#             return 0

# # Extract header from the 21st table
# header_row = tables[22].find('tr', class_='replinedown')
# headers = [header.text.strip() for header in header_row.find_all('div')]

# # Initialize an empty list to store the data
# data = []

# # Iterate through tables starting from index 21
# for table in tables[23:]:
#     rows = table.find_all('tr', class_='replinedown')
#     for row in rows:
#         # Extract row data
#         row_data = [cell.text.strip() for cell in row.find_all('div')]
#         # Append row data to the list
#         data.append(row_data)

df_agent_cc = pd.DataFrame(data, columns=headers)
print(df_agent_cc.columns)
# Convert string values to numeric in specified columns
df_agent_cc['Answered'] = df_agent_cc['Answered'].apply(convert_to_numeric)
df_agent_cc['Forwarded'] = df_agent_cc['Forwarded'].apply(convert_to_numeric)
df_agent_cc['Delegated ext'] = df_agent_cc['Delegated ext'].apply(convert_to_numeric)
df_agent_cc['Delegated int'] = df_agent_cc['Delegated int'].apply(convert_to_numeric)
df_agent_cc['Ignored'] = df_agent_cc['Ignored'].apply(convert_to_numeric)
df_agent_cc['Outbound'] = df_agent_cc['Outbound'].apply(convert_to_numeric)

# df_agent = df_agent.fillna(value="")
df_agent_cc['Total'] = df_agent_cc[['Answered', 'Forwarded', 'Delegated ext', 'Delegated int', 'Outbound']].sum(axis=1)
print(df_agent_cc.columns)
# Replace 0 with empty strings
df_agent_cc.replace(0, '', inplace=True)

# Converting the dataframe to image
# Specify custom column widths
df_agent_cc = df_agent_cc.fillna(value="")
# Specify custom column widths
col_widths = [4.0, 3.5, 2.0, 2.0, 2.5, 2.0, 2.0, 2.0, 2.0, 1.5]  # Adjust widths as needed
if not df_agent_cc.empty:
    render_mpl_table(df_agent_cc, col_widths=col_widths, header_columns=0)
    plt.savefig('CCProductivity.png')
else:
    print("DataFrame is empty. Skipping table rendering.")
    
import requests
from bs4 import BeautifulSoup
from IPython.display import display_html

# Define the cookies and headers
# cookies = {
#     'hs_userid': '105470',
#     'hs_ticket': 'RddYdMujqARktDKr5ZCdt1qSG%2BinqOiygz68ce4rw%2BCMX5ubS7silo2sYRd4n4%2BDUE1A23lAObOyG00osg8rOuWoEAJ%2B4wCx8yaKfnDS8JBGhQCUKOEqT4Wgihj6WO39eZmzeg%3D%3D',
#     'PHPSESSID': 'bc8imdkiq7rm391d2lkpkmqgr7',
# }

cookies = {
    'PHPSESSID': PHPSESSID,
    'hs_userid': hs_userid,
    'hs_ticket': hs_ticket,
}

headers_initial = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Referer': 'https://toolbox.leisure-group.eu/email/?action=search&direct=1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
    'sec-ch-ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

params_initial = {
    'action': 'setafd',
    'curr': 'L2VtYWlsLz9hY3Rpb249c2VhcmNoJmRpcmVjdD0x',
    'nafd': '6',
}

# Make the initial GET request
response = requests.get('https://toolbox.leisure-group.eu/', params=params_initial, cookies=cookies, headers=headers_initial, allow_redirects=False)

# Check if the response indicates a redirect
if response.status_code in [301, 302]:
    # Get the redirection URL from the 'Location' header
    redirect_url = response.headers.get('Location')

    if redirect_url:
        # Construct the full URL for the redirection
        full_redirect_url = requests.compat.urljoin('https://toolbox.leisure-group.eu', redirect_url)

        # Make the second GET request to the redirected URL
        final_response = requests.get(full_redirect_url, cookies=cookies, headers=headers_initial)

        # Check if the second request is successful
        if final_response.status_code == 200:
            # Parse the content of the final response
            soup = BeautifulSoup(final_response.content, "html.parser")
            # display_html(str(soup), raw=True)

            # Prepare for the third request
            headers_third = {
                'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
                'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://toolbox.leisure-group.eu',
                'Referer': 'https://toolbox.leisure-group.eu/email/?action=search&direct=1',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
                'X-Prototype-Version': '1.7.1',
                'X-Requested-With': 'XMLHttpRequest',
                'sec-ch-ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }

            params_third = {
                'action': 'ajax',
                'subaction': 'monitor',
                'short': '1',
            }

            # Make the third POST request
            third_response = requests.post('https://toolbox.leisure-group.eu/email/', params=params_third, cookies=cookies, headers=headers_third)

            # Check the third response and parse it
            if third_response.status_code == 200:
                soup_third = BeautifulSoup(third_response.content, "html.parser")
                # display_html(str(soup_third), raw=True)
            else:
                print(f"Third request resulted in status code: {third_response.status_code}")
        else:
            print(f"Second request resulted in status code: {final_response.status_code}")
    else:
        print("No redirection URL found.")
else:
    print("Initial request did not result in a redirect.")
    soup = BeautifulSoup(response.content, "html.parser")
    # display_html(str(soup), raw=True)

# Extracting the desired table
# Find all tables with class 'repline'
tables = soup_third.find_all('table', class_='repline')
# tables = soup.find_all('table', class_='repline')

def convert_to_numeric(value):
    if pd.isnull(value):
        return 0
    try:
        return int(float(value))
    except ValueError:
        try:
            return int(float(value))
        except ValueError:
            return 0

# Define the keywords to search for
keywords = ["Agent", "Time", "Answered", "Forwarded", "Delegated ext", "Delegated int", "Ignored", "Outbound"]

# Initialize variables to store the target table and index
target_table = None
target_index = -1

# Search for the table containing the desired keywords
for index, table in enumerate(tables):
    # Get all rows in the table
    rows = table.find_all('tr')
    for row in rows:
        # Check if any keyword is found in the row
        row_text = row.get_text(separator=' ').strip()  # Get the row text
        if any(keyword in row_text for keyword in keywords):
            target_table = table
            target_index = index
            break
    if target_table:  # Break outer loop if target table is found
        break

data = []
# Check if a table was found
if target_table:
    print(f"Target table found at index {target_index}")
    # Extract header from the 21st table
    header_row = tables[target_index].find('tr', class_='replinedown')
    headers = [header.text.strip() for header in header_row.find_all('div')]
    
    # Initialize an empty list to store the data
    
    # Iterate through tables starting from index 21
    for table in tables[target_index+1:]:
        rows = table.find_all('tr', class_='replinedown')
        for row in rows:
            # Extract row data
            row_data = [cell.text.strip() for cell in row.find_all('div')]
            # Append row data to the list
            data.append(row_data)
        
    # # Extract headers
    # header_row = target_table.find('tr', class_='replinedown')
    # headers = [header.text.strip() for header in header_row.find_all('div')]
    
    # # Extract data rows
    # data = []
    # data_rows = target_table.find_all('tr', class_='replinedown')
    # for row in data_rows:
    #     row_data = [cell.text.strip() for cell in row.find_all('div')]
    #     data.append(row_data)
    
    # Create a DataFrame
    df = pd.DataFrame(data, columns=headers)
    print(df)
else:
    print("Target table not found.")
# def convert_to_numeric(value):
#     if pd.isnull(value):
#         return 0
#     try:
#         return int(float(value))
#     except ValueError:
#         try:
#             return int(float(value))
#         except ValueError:
#             return 0

# # Extract header from the 21st table
# header_row = tables[6].find('tr', class_='replinedown')
# headers = [header.text.strip() for header in header_row.find_all('div')]

# # Initialize an empty list to store the data
# data = []

# # Iterate through tables starting from index 21
# for table in tables[7:]:
#     rows = table.find_all('tr', class_='replinedown')
#     for row in rows:
#         # Extract row data
#         row_data = [cell.text.strip() for cell in row.find_all('div')]
#         # Append row data to the list
#         data.append(row_data)

df_agent_prk = pd.DataFrame(data, columns=headers)
print(df_agent_prk.columns)
# Convert string values to numeric in specified columns
df_agent_prk['Answered'] = df_agent_prk['Answered'].apply(convert_to_numeric)
df_agent_prk['Forwarded'] = df_agent_prk['Forwarded'].apply(convert_to_numeric)
df_agent_prk['Delegated ext'] = df_agent_prk['Delegated ext'].apply(convert_to_numeric)
df_agent_prk['Delegated int'] = df_agent_prk['Delegated int'].apply(convert_to_numeric)
df_agent_prk['Ignored'] = df_agent_prk['Ignored'].apply(convert_to_numeric)
df_agent_prk['Outbound'] = df_agent_prk['Outbound'].apply(convert_to_numeric)

# df_agent = df_agent.fillna(value="")
df_agent_prk['Total'] = df_agent_prk[['Answered', 'Forwarded', 'Delegated ext', 'Delegated int', 'Outbound']].sum(axis=1)
print(df_agent_prk.columns)
# Replace 0 with empty strings
df_agent_prk.replace(0, '', inplace=True)

# Converting the dataframe to image
# Specify custom column widths
df_agent_prk = df_agent_prk.fillna(value="")
# Specify custom column widths
col_widths = [4.0, 3.5, 2.0, 2.0, 2.5, 2.0, 2.0, 2.0, 2.0, 1.5]  # Adjust widths as needed
if not df_agent_prk.empty:
    render_mpl_table(df_agent_prk, col_widths=col_widths, header_columns=0)
    plt.show()
    plt.savefig('Productivity_2.png')
else:
    print("DataFrame is empty. Skipping table rendering.")
    
import requests
from bs4 import BeautifulSoup
from IPython.display import display_html

# Define the cookies and headers
# cookies = {
#     'hs_userid': '105470',
#     'hs_ticket': 'RddYdMujqARktDKr5ZCdt1qSG%2BinqOiygz68ce4rw%2BCMX5ubS7silo2sYRd4n4%2BDUE1A23lAObOyG00osg8rOuWoEAJ%2B4wCx8yaKfnDS8JBGhQCUKOEqT4Wgihj6WO39eZmzeg%3D%3D',
#     'PHPSESSID': 'bc8imdkiq7rm391d2lkpkmqgr7',
# }

cookies = {
    'PHPSESSID': PHPSESSID,
    'hs_userid': hs_userid,
    'hs_ticket': hs_ticket,
}

headers_initial = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Referer': 'https://toolbox.leisure-group.eu/email/?action=search&direct=1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
    'sec-ch-ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

params_initial = {
    'action': 'setafd',
    'curr': 'L2VtYWlsLz9hY3Rpb249c2VhcmNoJmRpcmVjdD0x',
    'nafd': '1',
}

# Make the initial GET request
response = requests.get('https://toolbox.leisure-group.eu/', params=params_initial, cookies=cookies, headers=headers_initial, allow_redirects=False)

# Check if the response indicates a redirect
if response.status_code in [301, 302]:
    # Get the redirection URL from the 'Location' header
    redirect_url = response.headers.get('Location')

    if redirect_url:
        # Construct the full URL for the redirection
        full_redirect_url = requests.compat.urljoin('https://toolbox.leisure-group.eu', redirect_url)

        # Make the second GET request to the redirected URL
        final_response = requests.get(full_redirect_url, cookies=cookies, headers=headers_initial)

        # Check if the second request is successful
        if final_response.status_code == 200:
            # Parse the content of the final response
            soup = BeautifulSoup(final_response.content, "html.parser")
            # display_html(str(soup), raw=True)

            # Prepare for the third request
            headers_third = {
                'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
                'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://toolbox.leisure-group.eu',
                'Referer': 'https://toolbox.leisure-group.eu/email/?action=search&direct=1',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
                'X-Prototype-Version': '1.7.1',
                'X-Requested-With': 'XMLHttpRequest',
                'sec-ch-ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }

            params_third = {
                'action': 'ajax',
                'subaction': 'monitor',
                'short': '1',
            }

            # Make the third POST request
            third_response = requests.post('https://toolbox.leisure-group.eu/email/', params=params_third, cookies=cookies, headers=headers_third)

            # Check the third response and parse it
            if third_response.status_code == 200:
                soup_third = BeautifulSoup(third_response.content, "html.parser")
                # display_html(str(soup_third), raw=True)
            else:
                print(f"Third request resulted in status code: {third_response.status_code}")
        else:
            print(f"Second request resulted in status code: {final_response.status_code}")
    else:
        print("No redirection URL found.")
else:
    print("Initial request did not result in a redirect.")
    soup = BeautifulSoup(response.content, "html.parser")
    # display_html(str(soup), raw=True)

# Extracting the desired table
# Find all tables with class 'repline'
tables = soup_third.find_all('table', class_='repline')
# tables = soup.find_all('table', class_='repline')

def convert_to_numeric(value):
    if pd.isnull(value):
        return 0
    try:
        return int(float(value))
    except ValueError:
        try:
            return int(float(value))
        except ValueError:
            return 0

# Define the keywords to search for
keywords = ["Agent", "Time", "Answered", "Forwarded", "Delegated ext", "Delegated int", "Ignored", "Outbound"]

# Initialize variables to store the target table and index
target_table = None
target_index = -1

# Search for the table containing the desired keywords
for index, table in enumerate(tables):
    # Get all rows in the table
    rows = table.find_all('tr')
    for row in rows:
        # Check if any keyword is found in the row
        row_text = row.get_text(separator=' ').strip()  # Get the row text
        if any(keyword in row_text for keyword in keywords):
            target_table = table
            target_index = index
            break
    if target_table:  # Break outer loop if target table is found
        break

data = []
# Check if a table was found
if target_table:
    print(f"Target table found at index {target_index}")
    # Extract header from the 21st table
    header_row = tables[target_index].find('tr', class_='replinedown')
    headers = [header.text.strip() for header in header_row.find_all('div')]
    
    # Initialize an empty list to store the data
    
    # Iterate through tables starting from index 21
    for table in tables[target_index+1:]:
        rows = table.find_all('tr', class_='replinedown')
        for row in rows:
            # Extract row data
            row_data = [cell.text.strip() for cell in row.find_all('div')]
            # Append row data to the list
            data.append(row_data)
        
    # # Extract headers
    # header_row = target_table.find('tr', class_='replinedown')
    # headers = [header.text.strip() for header in header_row.find_all('div')]
    
    # # Extract data rows
    # data = []
    # data_rows = target_table.find_all('tr', class_='replinedown')
    # for row in data_rows:
    #     row_data = [cell.text.strip() for cell in row.find_all('div')]
    #     data.append(row_data)
    
    # Create a DataFrame
    df = pd.DataFrame(data, columns=headers)
    print(df)
else:
    print("Target table not found.")
# def convert_to_numeric(value):
#     if pd.isnull(value):
#         return 0
#     try:
#         return int(float(value))
#     except ValueError:
#         try:
#             return int(float(value))
#         except ValueError:
#             return 0

# # Extract header from the 21st table
# header_row = tables[75].find('tr', class_='replinedown')
# headers = [header.text.strip() for header in header_row.find_all('div')]

# # Initialize an empty list to store the data
# data = []

# # Iterate through tables starting from index 21
# for table in tables[76:]:
#     rows = table.find_all('tr', class_='replinedown')
#     for row in rows:
#         # Extract row data
#         row_data = [cell.text.strip() for cell in row.find_all('div')]
#         # Append row data to the list
#         data.append(row_data)

df_agent_cs = pd.DataFrame(data, columns=headers)
print(df_agent_cs.columns)
# Convert string values to numeric in specified columns
df_agent_cs['Answered'] = df_agent_cs['Answered'].apply(convert_to_numeric)
df_agent_cs['Forwarded'] = df_agent_cs['Forwarded'].apply(convert_to_numeric)
df_agent_cs['Delegated ext'] = df_agent_cs['Delegated ext'].apply(convert_to_numeric)
df_agent_cs['Delegated int'] = df_agent_cs['Delegated int'].apply(convert_to_numeric)
df_agent_cs['Ignored'] = df_agent_cs['Ignored'].apply(convert_to_numeric)
df_agent_cs['Outbound'] = df_agent_cs['Outbound'].apply(convert_to_numeric)

# df_agent = df_agent.fillna(value="")
df_agent_cs['Total'] = df_agent_cs[['Answered', 'Forwarded', 'Delegated ext', 'Delegated int', 'Outbound']].sum(axis=1)
print(df_agent_cs.columns)
# Replace 0 with empty strings
df_agent_cs.replace(0, '', inplace=True)
agent_names_cs = ["Dipanshu Verma", "Akanksha Tiwary", "Animesh Das", "Neelima Dhamenia", "Shefali Modi", "Rabi Gayan", "simranjeetkaur", "Hrishikesh Das", "Mayank Maheshwari", "Vaishali Singh", "Mogilicharla Karthik", "akankshaahlawat", "Mayank Kumar", "Aditya Singh Narwal", "Harprit Kaur", "Shrangarika Nagar"]
df_agent_cs = df_agent_cs[df_agent_cs['Agent'].isin(agent_names_cs)]
# Converting the dataframe to image
# Specify custom column widths
df_agent_cs = df_agent_cs.fillna(value="")
# Specify custom column widths
col_widths = [4.0, 3.5, 2.0, 2.0, 2.5, 2.0, 2.0, 2.0, 2.0, 1.5]  # Adjust widths as needed
if not df_agent_cs.empty:
    render_mpl_table(df_agent_cs, col_widths=col_widths, header_columns=0)
    plt.savefig('Productivity_gast.png')
else:
    print("DataFrame is empty. Skipping table rendering.")
def convert_to_numeric(value):
    if pd.isnull(value) or value == '':
        return 0
    try:
        return int(float(value))
    except ValueError:
        return 0

# Assuming df_agent_ind and df_agent_names are your DataFrames
# Combine DataFrames by passing them as a list to pd.concat()
combined_df = pd.concat([df_agent, df_agent_cc,df_agent_prk,df_agent_cs])

# Reset the index after concatenation
combined_df.reset_index(drop=True, inplace=True)

# Convert the relevant columns to numeric, coercing errors
combined_df['Answered'] = combined_df['Answered'].apply(convert_to_numeric)
combined_df['Forwarded'] = combined_df['Forwarded'].apply(convert_to_numeric)
combined_df['Delegated ext'] = combined_df['Delegated ext'].apply(convert_to_numeric)
combined_df['Delegated int'] = combined_df['Delegated int'].apply(convert_to_numeric)
combined_df['Outbound'] = combined_df['Outbound'].apply(convert_to_numeric)
combined_df['Ignored'] = combined_df['Ignored'].apply(convert_to_numeric)

# Calculate 'Total' column
combined_df['Total'] = combined_df[['Answered', 'Forwarded', 'Delegated ext', 'Delegated int', 'Outbound','Ignored']].sum(axis=1)

agent_names_combined = ["Dipanshu Verma", "Akanksha Tiwary", "Animesh Das", "Neelima Dhamenia", "Shefali Modi", "Rabi Gayan", "simranjeetkaur", "Hrishikesh Das", "Mayank Maheshwari", "Vaishali Singh", "Mogilicharla Karthik", "akankshaahlawat", "Mayank Kumar", "Aditya Singh Narwal", "Harprit Kaur", "Shrangarika Nagar"]
combined_df = combined_df[combined_df['Agent'].isin(agent_names_combined)]

combined_df = combined_df.drop_duplicates(subset=['Agent'])

# Replace 0 with empty strings
combined_df.replace(0, '', inplace=True)
render_mpl_table(combined_df, col_widths=col_widths, header_columns=0)
# plt.show()
plt.savefig('CCProductivity.png')
input_file = "CCProductivity.png"  # Path to the input file
base64_string = encode_file_to_base64_string(input_file)

headers = {
    'accept': 'application/json',
    'authorization': 'Bearer ' + key,
    'content-type': 'application/json',
}

# json_data = {
#     'to': '917406809635-1623399518@g.us',
#     'media': 'data:image/png;name=Productivity.png;base64,' + base64_string,
#     'caption': date + ' ' + hour + 'PM Productivity update',
# }

json_data = {
    'to': '120363026189391320@g.us',
    'media': 'data:image/png;name=Productivity.png;base64,' + base64_string,
    'caption': date + ' ' + hour + '00 hrs Productivity update',
}

response = requests.post('https://gate.whapi.cloud/messages/image', headers=headers, json=json_data)

# input_file = "L123.png"  # Path to the input file
# base64_string = encode_file_to_base64_string(input_file)
