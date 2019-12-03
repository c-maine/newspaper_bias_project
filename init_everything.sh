sudo apt install python-pip
pip install pymysql
pip install sqlalchemy

#python2 clear_aws_tables.py

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

cd image1
docker build -t francescooo/big_fill .

cd ../image2
docker build -t francescooo/daily_fill .

#run docker and then remove container that fills the tables with articles from the last 30 days
sudo docker run --name init francescooo/big_fill
sudo docker rm init

cd ../
#setup a cron job that runs the container that every day inserts in the databse articles from the previous day
crontab cron_setup


