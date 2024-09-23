import re
import pandas as pd

def preprocess(data):
    # Pattern for both 24-hour and AM/PM format dates
    pattern = '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[APM]*\s-\s'

    # Split messages and extract dates using the new pattern
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    # Create a dataframe with the extracted messages and dates
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Convert message_date to datetime, handling both formats
    df['message_date'] = pd.to_datetime(df['message_date'], format='%m/%d/%y, %I:%M %p - ', errors='coerce')
    # If any dates were not parsed in the AM/PM format, try the 24-hour format
    df['message_date'] = df['message_date'].fillna(pd.to_datetime(df['message_date'], format='%m/%d/%y, %H:%M - ', errors='coerce'))

    # Rename column
    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Split user and message
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Extract additional date/time features
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Create period ranges (hour-hour+1)
    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df
