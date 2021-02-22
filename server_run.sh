#!/bin/bash


cd ./Backend


# Setup DB or any other environment variables you want to setup.
python3 -c "from localapi import db; db.create_all();print('TABLE CREATED');"



# To run the api, which will run at port 8081
python3 ./localapi.py

# To run the webApp, which will run at port 8082
# python3 ./Frontend/main.py