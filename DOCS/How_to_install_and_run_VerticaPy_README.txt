# To install VerticaPy read the instructions here: https://www.vertica.com/python/installation.php
# Here is an example for what to do on the Ubuntu Linux server, as user root, where Vertica is already installed:
pip install jupyterlab
pip3 install verticapy[all]
pip install ipython-sql
pip install ipywidgets

# On the Linux server as dbadmin user:
jupyter lab --no-browser
# Later to shutdown this Jupyter server do: ^C 

# On a PC browser like Google Chrom, copy & paste the text token from the jupyter lab run output:
  http://Jupiter_lab_Linux_server_IP_address:8888/lab... 

# On your PC browser like Google Chrom / jupyter lab frontend, run the following in cell 1:
import verticapy as vp

# Creating a new connection to your Vertica Database
# On your PC browser like Google Chrom / jupyter lab frontend, run the following in cell 2: 
vp.new_connection({"host": "Your_Vertica_DB_server_IP_address", 
                   "port": "5433", 
                   "database": "Your_Database_name", 
                   "password": "Your_Database_password", 
                   "user": "dbadmin_or_your_Vertica_super_user_name"},
                   name = "MyVerticaConnection")

# Later to connect to the Database do the following, each statement in a separated Jupiter lab cell:
import verticapy as vp
vp.connect("MyVerticaConnection")
%load_ext verticapy.sql
