To run the server:


Ensure that ports 2399-2450 are open, depending on how many clients intend to connect. 
Ensure that port 5000 is also available for outgoing data. 

Enter the following commands within this director:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

If there are issues with the `pip install` command, ensure that you have the latest version of `pip`. 

To start the server, run `python3 app.py`.

If it is successful, you should see a "UDP Server Up and Listening" Message and also be able to access the website on `YOURIP:5000`


Pong.js code is modified based off Gabriel Dubé's Codepen "Pong with Javascript" - https://codepen.io/gdube/pen/JybxxZ
