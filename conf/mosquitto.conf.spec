persistence true
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log

listener 1883
## Authentication ##
allow_anonymous false
password_file /mosquitto/conf/mosquitto.conf