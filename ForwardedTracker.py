from BoilerPlate import *

excel_link1 = 'https://oyoenterprise-my.sharepoint.com/:x:/r/personal/kartikbangard1_wv_oyorooms_com/_layouts/15/Doc.aspx?sourcedoc=%7BAD388DB7-159D-463E-8D9E-21521668CF90%7D&file=Agent%20Productivity%20-%20HS.xlsx&fromShare=true&action=default&mobileredirect=true'
excel_link = 'https://oyoenterprise-my.sharepoint.com/:x:/r/personal/sayak_adak1_oyorooms_com/_layouts/15/Doc.aspx?sourcedoc=%7B0663CF9D-7D79-4FDD-8708-A63B79722C27%7D&file=ForwardedTracker.xlsx&fromShare=true&action=default&mobileredirect=true'

wb1 = WorkbookUnlocked(config=auth_config, url=excel_link1) # Source of Updated Agents
wb = WorkbookUnlocked(config=auth_config, url=excel_link) # Forwarded Tracker
tc = TeamsClient(config=auth_config)
cookies = {
    'hs_userid': cookies['hs_userid'],
    'hs_ticket': cookies['hs_ticket'],
    'PHPSESSID': cookies['PHPSESSID'],
}

# Update Agents list for scraping
df_agents = wb1.get_range_data('Ref', range_address='B:B', as_df=True)
wb.write_data(sheet_name='HS Agents', location='B1', df=df_agents)
data = wb.get_range_data('HS Agents',as_df = False)
headers = data[0]
rows = data[1:]
agent_ids = pd.DataFrame(rows, columns = headers)
agent_ids = agent_ids['ID']
agent_ids = agent_ids.replace("", float("NaN"))
agent_ids.dropna(inplace=True) 

# Get Last sent date to avoid processing dates from 1st Jan
def get_last_run_date():
    try:
        df_sent = wb.get_range_data('Sent', range_address='E:E', as_df=True)
        df_sent['Date'] = pd.to_datetime(df_sent['Date'], errors='coerce')
        last_date = df_sent['Date'].max()
        if pd.isnull(last_date):
            # if no valid dates, default to the start of the current year
            last_date = datetime(datetime.now().year, 1, 1)
    except Exception as e:
        print("Error retrieving last run date:", e)
        last_date = datetime(datetime.now().year, 1, 1)
    return last_date
last_run_date = get_last_run_date()
today = datetime.now()
print(f"Fetching new data from {last_run_date.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}")

# Scraping begins
all_sent_mails = []
for agent_id in agent_ids:
    print(f"Processing agent ID: {agent_id}")
    
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9,en-IN;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'https://toolbox.leisure-group.eu/email/?action=search&direct=1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Microsoft Edge";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    params = {
        'action': 'agentsentmail',
        'subaction': 'go',
        'van_dag': last_run_date.day,
        'van_maand': last_run_date.month,
        'van_jaar': last_run_date.year,
        'tot_dag': today.day,
        'tot_maand': today.month,
        'tot_jaar': today.year,
        'selected_user': agent_id,
    }
    
    try:
        response = requests.get('https://toolbox.leisure-group.eu/email/', params=params, cookies=cookies, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        # Extracting the table "Per agent (completed)" from the response page
        tables = soup.find_all('table', class_='table table-condensed table-bordered table-striped')
        if len(tables) == 0:
            print(f"No table found for agent ID: {agent_id}, skipping...")
            continue  # Skip to the next agent ID
        table = tables[0]
        headers = [header.text.strip() for header in table.find_all('th')]
        data = []
        for row in table.find_all('tr'):
            row_data = [cell.text.strip() for cell in row.find_all('td')]
            if row_data:
                data.append(row_data)
        sent_mails = pd.DataFrame(data, columns=headers)
        all_sent_mails.append(sent_mails)
    except Exception as e:
        print(f"Error processing agent ID {agent_id}: {e}")
        continue
if all_sent_mails:
    combined_sent_mails = pd.concat(all_sent_mails, ignore_index=True)
    print(combined_sent_mails)
else:
    print("No data found for any agents.")

# Update the list of all agents
options = soup.select('td.veldform select[name="selected_user"] option')
data = []
headers = ['ID', 'Agent']
for option in options:
    value = option.get('value')
    text = option.text.strip()
    row_data = [value, text]
    data.append(row_data)
data = data[1:]
agents = pd.DataFrame(data, columns=headers)
wb.write_data('All Agents',agents)

# Clean toolbox data
day_translation = {'Ma': 'Mon','Di': 'Tue','Wo': 'Wed','Do': 'Thu','Vr': 'Fri','Za': 'Sat','Zo': 'Sun'}
dates_series = combined_sent_mails['Date']
dates_series = dates_series.replace(day_translation, regex=True)
dates_series = dates_series.str.replace(r'\b([A-Za-z]{3})\.', r'\1', regex=True)
converted_dates = []
problematic_rows = []
for idx, date_str in enumerate(dates_series):
    try:
        converted_date = pd.to_datetime(date_str, format="%a %d %b '%y %H:%M")
        converted_dates.append(converted_date)
    except ValueError:
        problematic_rows.append((idx, date_str))
        converted_dates.append(None)
combined_sent_mails['Date'] = converted_dates
problematic_rows_df = pd.DataFrame(problematic_rows, columns=['Index', 'Original Date'])

sent = wb.get_range_data('Sent', as_df=False)
headers = sent[0]
rows = sent[1:]
df_sent = pd.DataFrame(rows, columns = headers)
summary_mails = wb.get_range_data('Summary', range_address='D:D', as_df=False)
headers = summary_mails[0]
rows = summary_mails[1:]
df_summary_mails = pd.DataFrame(rows, columns = headers)
wb.append_data('Answered',df_not_picked_up[df_not_picked_up['Solved'] == 'Yes'][['ID']])
summary_pocs = wb.get_range_data('Summary', range_address='C:C', as_df=False)
headers = summary_pocs[0]
rows = summary_pocs[1:]
df_summary_pocs = pd.DataFrame(rows, columns = headers)

# Combine the two columns into one Series of unique search terms
print(f"Problematic Rows: {problematic_rows_df}")
combined_search = pd.concat([df_summary_pocs['POC'], df_summary_mails['Mail']]).unique()
print(f"Original combined_sent_mails : {combined_sent_mails}")
print(f"Searching from : {combined_search}")
filtered_combined_sent_mails = combined_sent_mails[combined_sent_mails['To'].apply(
    lambda x: any(search_val in x for search_val in combined_search)
)]
print(f"Filtered combined_sent_mails : {filtered_combined_sent_mails}")
filtered_combined_sent_mails = filtered_combined_sent_mails[~filtered_combined_sent_mails['ID'].isin(df_sent['ID'])]
wb.append_data('Sent',filtered_combined_sent_mails)

formatted_agents = ",".join([f"'{x}'" for x in combined_search])
# formatted_agents
query = """
SELECT EMAIL_TYPE_NAME,EMAIL_ID,EMAIL,Follows,
EMAIL_RECEIVED_TIMESTAMP,EMAIL_ANSWERED_timestamp,
Extract(ISOWEEK from EMAIL_received_DATE) as Week,
Extract(Month from EMAIL_received_DATE) as Month,
Extract(Day from EMAIL_received_DATE) as Day,
Extract(Hour from EMAIL_RECEIVED_TIMESTAMP) as Hour,
EMAIL_STATUS_NAME,
CASE 
    WHEN EMAIL_QUEUE_NAME IN (' DE Box') THEN 'DE Box'
    WHEN EMAIL_QUEUE_NAME IN (' NL Box') THEN 'NL Box'
    WHEN EMAIL_QUEUE_NAME IN (' EN Box') THEN 'EN Box'
    WHEN EMAIL_QUEUE_NAME IN (' FR Box') THEN 'FR Box'
    WHEN EMAIL_QUEUE_NAME IN (' IT Box') THEN 'IT Box'
    WHEN EMAIL_QUEUE_NAME IN (' ES Box') THEN 'ES Box'
    WHEN EMAIL_QUEUE_NAME LIKE '%SOS%' THEN 'SOS'
    WHEN EMAIL_QUEUE_NAME LIKE '%Damage%' THEN 'Damage'
    WHEN EMAIL_QUEUE_NAME LIKE '%Complaints%' THEN 'Complaints'
    WHEN EMAIL_QUEUE_NAME LIKE '%Rebooking%' THEN 'Rebooking'
    WHEN EMAIL_QUEUE_NAME LIKE '%POST%' THEN 'POST'
    WHEN EMAIL_QUEUE_NAME LIKE '%Platinum%' THEN 'Platinum'
    WHEN EMAIL_QUEUE_NAME LIKE '%SDF%' THEN 'SDF'
    ELSE EMAIL_QUEUE_NAME
END AS EMAIL_QUEUE_NAME,
EMAIL_QUEUE_DEPARTMENT,EMAIL_QUEUE_LANGUAGE,
level1_reason_name,level2_reason_name,
level3_reason_name,level4_reason_name,
Email_labels,
EMAIL_AGENT,
(DATE_DIFF( EMAIL_ANSWERED_TIMESTAMP, EMAIL_RECEIVED_TIMESTAMP,hour)/24) as TAT,
CASE 
    WHEN EMAIL IN ('suruchi.sharma@oyorooms.com') THEN 'Business Finance'
    WHEN EMAIL IN ('hiteshsingh.wv@oyorooms.com','dhruv.kumar1@oyorooms.com','content.belvilla@oyorooms.com','shikhardhyani.wv@oyorooms.com','nitesh.chaudhary@oyorooms.com') THEN 'Central Supply'
    WHEN EMAIL IN ('vibhor.goyal@oyorooms.com','anuj.ganotra@oyorooms.com') THEN 'Revenue'
    WHEN EMAIL IN ('komal.srivastava@oyorooms.com','medha.vaishnav@oyorooms.com') THEN 'CS Team'
    WHEN EMAIL IN ('mitroi.cristina@belvilla.com','andreea.paslaru@belvilla.com','nikhilgupta.wv@oyorooms.com','ovh-escalation@igtsolutions.com') THEN 'Customer Care'
    WHEN EMAIL IN ('vishaakha.vij@oyorooms.com') THEN 'DACH7'
    WHEN EMAIL IN ('deveshtejani.wv@oyorooms.com') THEN 'Finance'
    WHEN EMAIL IN ('enasel.enasel@igtsolutions.com','kriti.garg@oyorooms.com','rent@belvilla.com') THEN 'HOS'
    WHEN EMAIL IN ('devanjali.rastogi@oyorooms.com','rahul.jain8@oyorooms.com','belvillacu@gmail.com') THEN 'Legal'
    WHEN EMAIL IN ('rajan.raj@oyorooms.com') THEN 'PMS'
    WHEN EMAIL IN ('partnerships@belvilla.com','himanshu.singh11@oyorooms.com','awesh.kumar@oyorooms.com') THEN 'Partnership'
    WHEN EMAIL IN ('abhishaan.gupta@oyorooms.com') THEN 'Tech'
    WHEN EMAIL IN ('sukhvinder.singh@oyorooms.com') THEN 'Traum'
    WHEN EMAIL IN ('papiya.guha1@oyorooms.com','saiyed.shujauddin@igtsolutions.com') THEN 'TUI CS'
    ELSE "None"
END AS Team_Responsible,
 FROM `leisure-bi.TABLEAU.TOOLBOX_EMAIL` where
EMAIL IN ({agents})
AND EMAIL_received_DATE between '2025-01-01' and current_date
"""
df_content = client.query(query.format(agents=formatted_agents)).to_dataframe()
df_content = df_content.astype(str)

wb.write_data('Content',df_content)

sent = wb.get_range_data('Sent', as_df=False)
headers = sent[0]
rows = sent[1:]
df_sent = pd.DataFrame(rows, columns = headers)

new_follows = wb.get_range_data('Answered',range_address = 'A:A',as_df = False)
headers = new_follows[0]
rows = new_follows[1:]
df_new_follows = pd.DataFrame(rows, columns = headers)

ids_not_in_follows = df_sent[~df_sent['ID'].isin(df_content['Follows']) & ~df_sent['ID'].isin(df_new_follows['Answered'])].drop_duplicates()

df_notpicked = ids_not_in_follows.copy()
df_ids = df_notpicked['ID'].astype(str).tolist()
email_ids_str = ", ".join(f"'{email_id}'" for email_id in df_ids)

query2 = f"""
DECLARE email_ids ARRAY<STRING>;
SET email_ids = [{email_ids_str}];

WITH RECURSIVE
  InitialEmails AS (
    SELECT email_id AS start_email, email_id, follows
    FROM `leisure-bi.TABLEAU.TOOLBOX_EMAIL`
    WHERE email_id IN UNNEST(email_ids)
  ),
  TreeUp AS (
    SELECT start_email, email_id, follows FROM InitialEmails
    UNION ALL
    SELECT tu.start_email, t.email_id, t.follows
    FROM `leisure-bi.TABLEAU.TOOLBOX_EMAIL` t
    JOIN TreeUp tu ON t.email_id = tu.follows
  ),
  Root AS (
    SELECT start_email, email_id AS root_id FROM TreeUp WHERE follows = '0'
  ),
  TreeDown AS (
    SELECT r.start_email, t.email_id, t.follows
    FROM Root r
    JOIN `leisure-bi.TABLEAU.TOOLBOX_EMAIL` t ON t.email_id = r.root_id
    UNION ALL
    SELECT td.start_email, t.email_id, t.follows
    FROM `leisure-bi.TABLEAU.TOOLBOX_EMAIL` t
    JOIN TreeDown td ON t.follows = td.email_id
  )
SELECT DISTINCT td.start_email, td.email_id
FROM TreeDown td
JOIN `leisure-bi.TABLEAU.TOOLBOX_EMAIL` t ON td.email_id = t.email_id
-- WHERE t.EMAIL_RECEIVED_TIMESTAMP >= (
--   SELECT MAX(EMAIL_RECEIVED_TIMESTAMP)
--   FROM `leisure-bi.TABLEAU.TOOLBOX_EMAIL` te
--   WHERE te.email_id = td.start_email
--)
ORDER BY td.start_email;
"""

df = client.query(query2).to_dataframe()

# Check which emails received replies
ids_in_follows = df[df['email_id'].isin(df_content['Follows'])].drop_duplicates()

# Prepare and append data
if not ids_in_follows.empty:
    replied_emails = ids_in_follows['start_email'].unique()
    df_email = pd.DataFrame(replied_emails, columns=["email_id"])
    wb.append_data('Answered', df_email)

# Print messages for emails that didn't get replies
no_reply_emails = set(df_ids) - set(ids_in_follows['start_email'])
for email_id in no_reply_emails:
    print(f"None of the children of {email_id} has gotten a reply")

new_follows = wb.get_range_data('Answered',range_address = 'A:A',as_df = False)
headers = new_follows[0]
rows = new_follows[1:]
df_new_follows = pd.DataFrame(rows, columns = headers)

ids_not_in_follows = ids_not_in_follows[~ids_not_in_follows['ID'].isin(df_new_follows['Answered'])].drop_duplicates()

# ids_not_in_follows = ids_not_in_follows.drop(columns=['Match'])
ids_not_in_follows['Date'] = pd.to_datetime(ids_not_in_follows['Date'], errors='coerce')

# Handle invalid dates and calculate the 'Ageing' column
today = pd.Timestamp.now().normalize()  # Get today's date without time

# Ensure 'Date' is a pandas datetime object and subtract it from today's date
# Add 1 day to the difference (if you want to shift the ageing by 1 day)
ids_not_in_follows['Ageing'] = (today - ids_not_in_follows['Date'] + pd.Timedelta(days=1)).dt.days
ids_not_in_follows['Solved'] = "No"

wb.clear_range('Not picked up')
wb.clear_range('Not picked up')
wb.write_data('Not picked up',ids_not_in_follows)

# Teams Message
target_id = '19:8ac453260c10498fa74f03e963d14bf4@thread.v2'
chat_members = []
for chat in tc.get_chat_list():
    if chat.get('id') == target_id:
        # Found the matching chat, now extract name and email for each member
        chat_members = chat.get('members', [])

summary_data = wb.get_range_data('Summary', range_address='C:E', as_df=False)
headers = summary_data[0]
rows = summary_data[1:]
df_summary_data = pd.DataFrame(rows, columns = headers)
df_summary_data['Emails Pending'] = pd.to_numeric(df_summary_data['Emails Pending'], errors='coerce')
tagging_df = df_summary_data[df_summary_data['Emails Pending'] > 0][:len(df_summary_data[df_summary_data['Emails Pending'] > 0])-1]

tagged_emails = []
for _, row in tagging_df.iterrows():
    for member in chat_members:
        # Check if either the name or the email from the dataframe matches the chat member.
        if row['POC'] in member['name'] or row['Mail'] == member['email']:
            tagged_emails.append(f"$TAG({member['email']})")
            # Once a match is found, no need to check the remaining chat members for this row.
            break

# Join the tags into the desired final message.
final_message = "Kindly close the mails against your name " + ",".join(tagged_emails)
tc.send_message(final_message,chat_id=target_id)
