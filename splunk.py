import urllib.request
import ssl, time, platform, json
from configparser import ConfigParser

def send_event(splunk_host, splunk_port, auth_token, log_data):

   """Sends an event to the HTTP Event collector of a Splunk Instance"""
   
   try:
      # Integer value representing epoch time format
      event_time = time.time()
      
      # String representing the host name or IP
      host_id = platform.node()
      
      # String representing the Splunk sourcetype, see:
      # docs.splunk.com/Documentation/Splunk/6.3.2/Data/Listofpretrainedsourcetypes
      source_type = "access_combined"
      
      # Create request URL
      request_url = "https://%s:%i/services/collector" % (splunk_host, splunk_port)
      
      post_data = {
         "time": event_time, 
         "host": host_id,
         "sourcetype": source_type,
         "event": log_data
      }
      
      # Encode data in JSON utf-8 format
      data = json.dumps(post_data).encode('utf8')
      
      # Create auth header
      auth_header = "Splunk %s" % auth_token
      headers = {'Authorization' : auth_header}
      
      # Create request
      # Avoid Self signed errors
      ctx = ssl.create_default_context()
      ctx.check_hostname = False
      ctx.verify_mode = ssl.CERT_NONE

      req = urllib.request.Request(request_url, data, headers)
      response = urllib.request.urlopen(req, context=ctx)
      
      # read response, should be in JSON format
      read_response = response.read()
      
      try:
         response_json = json.loads(str(read_response)[2:-1])
         
         if "text" in response_json:
            if response_json["text"] == "Success":
               post_success = True
            else:
               post_success = False
      except:
         post_success = False
      
      if post_success == True:
         # Event was recieved successfully
         print ("Event was recieved successfully")
      else:
         # Event returned an error
         print ("Error sending request.")
      
   except Exception as err:
      # Network or connection error
      post_success = False
      print ("Error sending request")
      print (str(err))

   return post_success

def main():
    config = ConfigParser()
    config.read('mqtt.conf')
    splunk_host = config.get('Splunk','url')
    splunk_port = config.getint('Splunk','port')
    splunk_auth_token = config.get('Splunk','token')

    log_data = {
        "data_point_1": 50,
        "data_point_2": 20,
    }

    result = send_event(splunk_host, splunk_port, splunk_auth_token, log_data)
    print (result)

main()