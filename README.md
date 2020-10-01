# DQM-Log-Replay-Testing
For CERN's DQM Backend

To access the script:
(from lxplus) ssh root@188.185.90.225
cd /data/logproject

Currently running 2 screens, one for backend, one for requests replaying.
screen -ls
should see the name and id of the screen
screen -r (id)
To run: python3 request_replay.py (make sure you have a version of backend running on the machine)
To run dqmgui backend:
su dqmgui
cd ~/CMSSW_11_1_0_pre6/src
Cmsenv
dqmguibackend.sh

Results are written in the file failed_requests.txt (Requests with status code other than 200, invalid URL probably due to some weird encoding of UNIX, corrupted weblog file, ...)
Modify in source code file request_replay.py to choose which endpoints to test and which to ignore
Local version of the weblog is stored in /data/logproject/archivedlogs for faster accessing, if needed maybe we can write a script to periodically update the log
