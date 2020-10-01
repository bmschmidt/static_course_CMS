from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient import http
import datetime
import shelve


# Downloads all the the documents beginning with 'Week ' and moves them to the lectures folder. Probably only useful
# In the context of Bostonography.

modtimes = shelve.open("scripts/googledocstimes.shelf", "c")

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive.readonly']

def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '/home/bschmidt/Dropbox/credentials.json', SCOPES)
            creds = flow.run_local_server(port=9797)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    results = service.files().list(
        pageSize=20, fields="nextPageToken, files(id, name, modifiedTime)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        now = datetime.datetime.now()
        for item in items:
            modTime = datetime.datetime.strptime(item["modifiedTime"][:16],  "%Y-%m-%dT%H:%M")

            if "Week" in item['name']:
                if item['id'] in modtimes and modtimes[item['id']] >= modTime:
                    print("ignoring {} from {}".format(item['name'], item['modifiedTime']))
                    # ignore old files.
                    continue                
                if True:
                    file_id = item['id']
                    request = service.files().export_media(fileId=file_id,
                                             mimeType='text/plain')                    
                    fh = open("Lectures/{}.md".format(item['name'].replace(" ", "_").strip("Week_")), "wb")
                    downloader = http.MediaIoBaseDownload(fh, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        print("Download %d%%." % int(status.progress() * 100))
                    modtimes[item['id']] = modTime
                print(u'Downloaded {0} ({1})'.format(item['name'], item['id']))

if __name__ == '__main__':
    main()
    modtimes.close()
