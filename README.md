# Scoring-Tool
Welcome to the **Scoring-Tool** repository! This README will guide you through the setup and usage of the project. Follow these steps to get your development environment up and running smoothly.

This project is a fully-dockerized tool to score images by different users for scientific purpose. It's a [redcore](https://github.com/RedCore161/redcore "redcore")-derivative. It connects:

* Backend: Django using rest_framework
* Frontend: React
* Database: Postgres
* Reverse-Proxy: Nginx

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed on your system:

- Docker
- Python
- Node.js and npm


Add some URLs to your hosts-file, so they are locally available!

**Unix**

   ```sh
   sudo tee -a /etc/hosts > /dev/null <<EOT
   
   127.0.0.1 api.scoring.local
   127.0.0.1 scoring.local   
  
   EOT
   ```

**Windows:**
1. Shame on you for using should a bad OS!
2. Your host-file is at:
   ```sh
   %windir%\System32\drivers\etc
   ```
3. Copy the above code (between EOT) and save the file


## Setup Instructions

1. **Copy environment templates:**

   ```sh
   cp .env.template .env
   cp django.template django.env
   ```


2. **Edit the environment files as needed:**

    Open .env and django.env in your favorite text editor and configure them according to your requirements.

3. **Start the Docker containers:**
   This will start all necessary services in the background.
   ```sh
    docker compose up -d
   ```

## Local Development
### Backend

To start the local backend server, follow these steps:

1. **Apply migrations:**

   ```sh
    python manage.py makemigrations
    python manage.py migrate
   ```

2. **Create a superuser:**
   
   This command will prompt you to enter details for the admin user.
   ```sh
    python manage.py createadmin
   ```

3. **Start backend-server:**
   ```sh
    python manage.py runserver localhost:8000
    ```
### Frontend

To start the local frontend server, follow these steps:
   ```sh
    cd frontend
    npm install
    npm start
   ```

This will open a browser with the frontend visible.

[comment]: <> (## License)
[comment]: <> (This project is licensed under the MIT License. See the LICENSE file for more details.)

## Securing your webserver with firewall (off-topic)
If you run this on an accessible webserver (aka without VPN), you should secure it by only allowing the needed ports. i got you covered!

   ```sh
   # Install UFW on Debian/Ubuntu-based systems
   sudo apt-get update
   sudo apt-get install ufw
   
   # Install UFW on RHEL/CentOS-based systems
   sudo yum install epel-release
   sudo yum install ufw
   
   # Enable UFW
   sudo ufw enable
   
   # Allow ports 22 (SSH), 80 (HTTP), and 443 (HTTPS)
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   
   # Deny all other incoming traffic
   sudo ufw default deny incoming
   
   # Allow all outgoing traffic
   sudo ufw default allow outgoing
   
   # Reload UFW to apply the changes
   sudo ufw reload
   
   # Check UFW status
   sudo ufw status
   ```

Output should look like this:
   ```
   Status: active
   
   To                         Action      From
   --                         ------      ----
   22/tcp                     ALLOW       Anywhere
   80/tcp                     ALLOW       Anywhere
   443/tcp                    ALLOW       Anywhere
   22/tcp (v6)                ALLOW       Anywhere (v6)
   80/tcp (v6)                ALLOW       Anywhere (v6)
   443/tcp (v6)               ALLOW       Anywhere (v6)
   ```

Still, this project does not yet support HTTPS. But you can using [Certbot](https://certbot.eff.org/)


## Contact

For any inquiries or issues, please open an issue on GitHub

Happy coding! 🎉🚀
