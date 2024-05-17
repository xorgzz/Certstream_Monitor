How to use?<br>
<code>$ python3 run.py (filter file)</code><br>
<code>$ python3 run.py (filter file) --debug/-d</code><br>
(The debug option allows you to start the monitor without sending emails.)<br>
<br>
(Example usage of the software)<br>
<code>$ python3 run.py filters.txt</code>
<br>
<br>
The <code>run.py</code> file installs the necessary libraries that are not automatically installed with the Python3 interpreter.
<br>
<br>
The <code>app.py</code> file is the software for monitoring and filtering Certstream.<br>
<br>
To use the option for sending notifications and information via email, you need to fill out the email.json file:
```
{
    "sender_email": "your.address@email.com",
    "password": "passw0rd",
    "recipient_email": "recipient.address@email.com",
    "smtp_server": "smtp.server",
    "smtp_port": 465
}
```
<br>
The filtering results are automatically saved using <code>sqlite3</code> to the <code>logs.db</code> file.
<br>
<br>
A preview of the <code>logs.db</code> database is available through a web browser at <code>http://127.0.0.1:51820</code>. (<code>127.0.0.1</code> or the server address where the software is running)