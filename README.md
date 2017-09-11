# Music-catalog-app 
An item web application that provides a list of products within a variety of categories as well as provides a user registration and authentication system. 
Registered users have the ability to post, edit and delete their own products.

### Usage 
1) Clone the repository. 
2) Install VirtualBox
3) Install Vagrant
5) Move the catalog app into the vagrant directory
>Use the terminal to CD into vagrant, then use the follwing commands to configure and populate the database: 
- `vagrant up`
- `vagrant ssh`
- `cd /vagrant`
- `python database_setup.py`
- `python populatedb.py`
7) Run `python application.py`, then with your broswer visit localhost:8000 to view the website.
