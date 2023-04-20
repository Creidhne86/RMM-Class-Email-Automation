import base64
import logging
import requests
from datetime import datetime, timezone, timedelta

logging.basicConfig(filename='rmm_email_automation.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_access_token(api_key):
    
    """Obtains and returns an access token for the Wild Apricot API."""
    api_base_url = 'https://api.wildapricot.org/v2.2'
    auth_url = 'https://oauth.wildapricot.org/auth/token'

    # Encode the API key in base64 format
    encoded_key = base64.b64encode(f'APIKEY:{api_key}'.encode()).decode()

    # Set the headers for authentication
    auth_headers = {
        'Authorization': f'Basic {encoded_key}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    # Obtain the access token
    auth_data = {'grant_type': 'client_credentials', 'scope': 'auto'}
    auth_response = requests.post(auth_url, headers=auth_headers, data=auth_data)
    access_token = auth_response.json()['access_token']

    return access_token

def get_event_attendees(event_id, access_token):
    """Retrieves event details from the Wild Apricot API given an event ID and prints the number of checked-in attendees."""
    api_base_url = 'https://api.wildapricot.org/v2.2'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    # Make an API request to retrieve the account details
    account_response = requests.get(f'{api_base_url}/accounts', headers=headers)
    if account_response.status_code != 200:
        logging.error(f'Error: Unable to retrieve account details. Status code: {account_response.status_code}')
        return

    account_id = account_response.json()[0]['Id']

    # Make an API request to retrieve event registrations
    registrations_response = requests.get(
        f'{api_base_url}/accounts/{account_id}/eventregistrations?eventId={event_id}', headers=headers
    )
    if registrations_response.status_code != 200:
        logging.error(f'Error: Unable to retrieve event registrations. Status code: {registrations_response.status_code}')
        return

    registrations = registrations_response.json()

    # Print the individual contact IDs
    contact_ids = [registration['Contact']['Id'] for registration in registrations]
    #logging.info(f'Contact IDs: {contact_ids}')

    return contact_ids

def get_contact_info(contact_id, access_token):
    """Retrieves the email address and first name of a contact given a contact ID."""
    api_base_url = 'https://api.wildapricot.org/v2.1'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    # Make an API request to retrieve the account details
    account_response = requests.get(f'{api_base_url}/accounts', headers=headers)
    if account_response.status_code != 200:
        logging.error(f'Error: Unable to retrieve account details. Status code: {account_response.status_code}')
        return

    account_id = account_response.json()[0]['Id']

    # Make an API request to retrieve the contact details
    contact_response = requests.get(f'{api_base_url}/accounts/{account_id}/contacts/{contact_id}', headers=headers)
    if contact_response.status_code != 200:
        logging.info(f'Error: Unable to retrieve contact details. Status code: {contact_response.status_code}')
        return

    contact_details = contact_response.json()

    # Get the email address, first name, and membership status from the contact details
    email = contact_details.get('Email', 'Unknown')
    first_name = contact_details.get('FirstName', 'Unknown')
    membership_enabled = contact_details.get('MembershipEnabled', False)

    return email, first_name, contact_id, membership_enabled

def send_email(access_token,body, contact_id,first_name, email):


    """Sends a test email using the Wild Apricot API."""
    api_base_url = 'https://api.wildapricot.org/v2.2'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    account_response = requests.get(f'{api_base_url}/accounts', headers=headers)
    if account_response.status_code != 200:
        logging.error(f'Error: Unable to retrieve account details. Status code: {account_response.status_code}')
        return

    account_id = account_response.json()[0]['Id']

    # Prepare email data
    email_data = {
        "Subject": "Free Month Promo at Red Mountain Makers!",
        "Body": body,
        "ReplyToAddress": "secretary@redmountainmakers.org",
        "ReplyToName": "Red Mountain Makers",
        "Recipients": [
            {
                "Id": contact_id,
                "Type": "IndividualContactRecipient",
                "Name": first_name,
                "Email": email,
            }
        ],
    }


    # Make an API request to send the email
    send_email_response = requests.post(f'{api_base_url}/rpc/{account_id}/email/SendEmail', headers=headers, json=email_data)
    
    if send_email_response.status_code != 200:
        logging.error(f'Error: Unable to send email. Status code: {send_email_response.status_code}')
        return
    
def fill_email_template(Contact_First_Name, Event_Title,Discount_Code, template):
    return template.format(Contact_First_Name=Contact_First_Name, Event_Title=Event_Title, Discount_Code=Discount_Code)

def read_template_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def event_title(event_id, access_token):
    """Retrieves event details from the Wild Apricot API given an event ID and prints the number of checked-in attendees."""
    api_base_url = 'https://api.wildapricot.org/v2.2'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    # Make an API request to retrieve the account details
    account_response = requests.get(f'{api_base_url}/accounts', headers=headers)
    if account_response.status_code != 200:
        logging.error(f'Error: Unable to retrieve account details. Status code: {account_response.status_code}')
        return

    account_id = account_response.json()[0]['Id']

    # Make an API request to retrieve event details
    event_response = requests.get(f'{api_base_url}/accounts/{account_id}/Events/{event_id}', headers=headers)
    if event_response.status_code != 200:
        logging.error(f'Error: Unable to retrieve event details. Status code: {event_response.status_code}')
        return

    event_details = event_response.json()

    # Return the number of checked-in attendees
    event_name = event_details.get('Name', 'Unknown')
    return event_name

def get_past_event_ids(access_token, current_datetime=None):
    """Retrieves past public event data from the Wild Apricot API and returns a list of event IDs."""
    api_base_url = 'https://api.wildapricot.org/v2.2'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    # Make an API request to retrieve the account details
    account_response = requests.get(f'{api_base_url}/accounts', headers=headers)
    account_id = account_response.json()[0]['Id']

    # Get the current date and time, if not provided
    if current_datetime is None:
        current_datetime = datetime.now(timezone.utc)

    # Check if today is Monday
    hours_to_check = 72 if current_datetime.weekday() == 0 else 24
    past_datetime = current_datetime - timedelta(hours=hours_to_check)

    # Make an API request to retrieve event data
    events_response = requests.get(f'{api_base_url}/accounts/{account_id}/Events', headers=headers)
    events = events_response.json()['Events']

    # Filter events that occurred within the specified time frame, are visible to the public, and do not have "free" or "awa" in the title
    past_event_ids = [event['Id'] for event in events if event.get('EndDate') is not None and
                      past_datetime <= datetime.fromisoformat(event['EndDate'].replace('Z', '+00:00')) < current_datetime and
                      event.get('AccessLevel') == 'Public' and
                      'free' not in event.get('Name', '').lower() and
                      'awa' not in event.get('Name', '').lower()]

    return past_event_ids

def send_discount_emails(access_token, event_id_list, template_file_path, Discount_Code):
    html_template = read_template_file(template_file_path)
    num_emails = 0
    for event_id in event_id_list:

        print(event_id)
        Event_Title = event_title(event_id, access_token)
        contact_ids = get_event_attendees(event_id, access_token)

        if not contact_ids:
            print(f'No attendees found for event {event_id}')
        else:
            for id in contact_ids:
                contact_info = get_contact_info(id, access_token)
                membership_enabled = contact_info[3]

                # Skip over members
                if membership_enabled:
                    print("This person is already a member!")
                    continue

                num_emails += 1
                email = contact_info[0]
                Contact_First_Name = contact_info[1]
                contact_id = contact_info[2]
                logging.info(f" Found past event: {Event_Title}")
                # print(Contact_First_Name)
                # print(email)
                filled_template = fill_email_template(Contact_First_Name, Event_Title, Discount_Code, html_template)
                send_email(access_token, filled_template, contact_id, Contact_First_Name, email)
    logging.info(f'Sent {num_emails} emails.')
