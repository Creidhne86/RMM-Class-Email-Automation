import os
from datetime import datetime, timezone
from class_email_functions import*

api_key = os.environ.get("API_KEY")#Gets the API key from the environment variables
Discount_Code = os.environ.get("DISCOUNT_CODE")#Gets the discount code from the environment variables
access_token = get_access_token(api_key)#Gets the access token from the WA API

template_email_file_path = 'class_discount_email_template.html'

test_date = datetime(2024, 1, 1, tzinfo=timezone.utc)

event_id_list = get_past_event_ids(access_token,test_date)

send_discount_emails(access_token, event_id_list, template_email_file_path, Discount_Code)
