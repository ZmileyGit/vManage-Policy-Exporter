# vManage-Policy-Exporter
Tool for exporting and importing Centralized and Localized policies to/from a Cisco vManage.
## Getting started
These instructions will help you getting up and running with the script's functionalities.
### Prerequisites
Validate that you are using a release of Python 3.
```
python -V
```
Install the script's dependencies.
```
pip install -r requirements.txt
```
### Usage
Export the Centralized Policies from a vManage.
```
python export.py
Host: <IP address or Hostname>
Port(443): <Port number>
Certificate Check[y/n]: <y/n>
Username: <vManage username>
Password: <vManage user password>
(...)
Working File(policies.json): <Destination File>
```
Import the Centralized Policies from another vManage
```
python import.py
Working File(policies.json): <Source File>
Host: <IP address or Hostname>
Port(443): <Port number>
Certificate Check[y/n]: <y/n>
Username: <vManage username>
Password: <vManage user password>
(...)
```
### Examples
Export the Centralized Policies from a vManage with untrusted certificates.
```
python -W ignore export.py
Host: 10.0.0.1
Port(443): 8443
Certificate Check[y/n]: n
Username: admin
Password: *****
(...)
Working File(policies.json): lab_policies.json
```
Import the Centralized Policies from another vManage to a vManage with untrusted certificates.
```
python -W ignore import.py
Working File(policies.json): lab_policies.json
Host: 10.0.0.2
Port(443): 443
Certificate Check[y/n]: n
Username: admin
Password: *****
(...)
```