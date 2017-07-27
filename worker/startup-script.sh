git clone https://github.com/Alexander-Minyushkin/aistreamer.git
cd aistreamer/
cd worker/
sudo apt-get update
sudo apt-get install python-pip
sudo pip install --upgrade pip
sudo pip install google-cloud
sudo pip install luigi
sudo pip install -r requirements.txt
python main.py pubsub_pull
