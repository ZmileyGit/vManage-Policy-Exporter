# vManage-Policy-Exporter
Tool for exporting and importing Centralized and Localized policies to/from a Cisco vManage.
## Getting started
These instructions will help you getting up and running with the script's functionalities.
### Prerequisites
Validate that you are using a release of Python 3.7 or higher.
```
python -V
```
Install the script's dependencies.
```
pip install -r requirements.txt
```
### Usage for Centralized Policies
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
### Examples for Centralized Policies
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
### Usage for Localized Policies
Export the Localized Policies from a vManage.
```
python export-local.py
Host: <IP address or Hostname>
Port(443): <Port number>
Certificate Check[y/n]: <y/n>
Username: <vManage username>
Password: <vManage user password>
(...)
Working File(policies.json): <Destination File>
```
Import the Localized Policies from another vManage
```
python import-local.py
Working File(policies.json): <Source File>
Host: <IP address or Hostname>
Port(443): <Port number>
Certificate Check[y/n]: <y/n>
Username: <vManage username>
Password: <vManage user password>
(...)
```
### Examples for Localized Policies
Export the Localized Policies from a vManage with untrusted certificates.
```
python -W ignore export-local.py
Host: 10.0.0.1
Port(443): 8443
Certificate Check[y/n]: n
Username: admin
Password: *****
(...)
Working File(policies.json): lab_policies.json
```
Import the Localized Policies from another vManage to a vManage with untrusted certificates.
```
python -W ignore import-local.py
Working File(policies.json): lab_policies.json
Host: 10.0.0.2
Port(443): 443
Certificate Check[y/n]: n
Username: admin
Password: *****
(...)
```