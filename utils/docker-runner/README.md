Goal here is to create a script which would be used by GreenTea to run Beaker tests in docker image.

 1. playbook connects to a docker host defined in the inventory.ini
 2. builds a image if it is not there already
 3. creates an container
 4. runs the tests in the container and gathers results and logs
 5. places all the logs into directory structure from where GreenTea collector script loads them later

Usage
-----

    # ansible-playbook -i inventory.ini greentea-docker-luncher.yaml -e "job_id=12345 job_xml_file=example.xml"
