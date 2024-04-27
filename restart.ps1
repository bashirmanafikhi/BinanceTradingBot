# Define server details
$SERVER_USER = "root"
#$SERVER_USER = "bashir-ssh"
$SERVER_HOST = "93.127.202.191"
$SERVER_PATH = "/home/videostatuses/htdocs/videostatuses.com/"

# SSH into the server and run commands
$SSHCommand = @"
    # Navigate to the server path
    cd $SERVER_PATH

    # Activate the virtual environment
    source venv/bin/activate

    # set environment variable
    export FLASK_ENV=production

    cd app

    # Check if the process is running on port 5000
    # lsof -i :5000
    if lsof -t -i :5000 > /dev/null 2>&1; then
        # If running, find and kill the existing process
        lsof -t -i :5000 | xargs kill -9
    fi

    # Start Gunicorn in the background
    gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:5000 run_web:app --log-level info --error-logfile log/gunicorn_error.log --capture-output -D
    #gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:5000 run_web:app
"@

# Run SSH command
ssh -i "~/.ssh/id_rsa" "$SERVER_USER@$SERVER_HOST" "$SSHCommand"
