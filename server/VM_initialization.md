1. Install Node and NPM
  ```
  curl -sL https://deb.nodesource.com/setup_10.x | sudo bash -
  sudo apt install nodejs
  ```
2. Clone Git repo
  ```
  sudo git clone https://github.com/ehiggins98/EECS448-Project-3.git
  ```
3. Edit the crontab to redirect traffic from port 80 to 8080 and start the server
	```
	sudo crontab -e
	```
4. Add the following line to the crontab. This redirects traffic from port 80 to 8080.
	```
	@reboot sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080 2>&1
	```
5. Edit the user's crontab
	```
	sudo crontab -e -u ericdhiggins
	```
6. Add the following line to that crontab. It starts the Node server
	```
	@reboot /usr/bin/node /home/ericdhiggins/EECS448-Project-3/server/worker.js 2>&1
	```