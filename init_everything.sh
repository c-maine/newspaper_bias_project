sudo apt install python-pip
pip install pymysql
pip install sqlalchemy

#Install docker and pull the two images
sudo apt-get remove docker docker-engine docker.io containerd runc

sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo apt-key fingerprint 0EBFCD88

sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io

#cd docker_image
docker pull francescooo/news_project

#run docker and then remove container that fills the tables with articles from the last 30 days
sudo docker run -v /home/ubuntu/newspaper_bias_project/useful_files:/home --name im --rm francescooo/news_project

cd ./useful_files
#setup a cron job that runs the container that every day inserts in the databse articles from the previous day
crontab cron_setup

cd ../dash/image_dashboard
sudo docker build -t francescooo/dash_server .

sudo docker run -v /home/ubuntu/newspaper_bias_project/dash_for_project/assets:/home/assets -p 80:8050 --name dash -d francescooo/dash_server