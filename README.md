To run my project on your own computer you need to open the final-project folder in a text editor.

Once in the text editor you should go to the final project directory by typing in the terminal: cd final-project

Once in in the proper directory you will need to create a virtual environment and install some libraries within the virtal environment. Outside of the virtual environment, you should have sqlite3 and datetime installed. You can install them by typing this command: pip3 install "name of library you want installed" 
All of the libraries that should be installed in the virtual environment can be found in the requirements.txt file. They should be installed using the same command as above. 

The instructions to create a virtual environment can be found here: https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-local-programming-environment-on-ubuntu-20-04

To make things clear, however, you can just type this code in this order:

sudo apt install -y python3-venv

python3 -m venv venv



To activate the virtual environment named "venv" you should type: source venv/bin/activate

Once activated you should install all of the libraries in the requirements.txt file.

After these libraries are installed you should type these commands into the terminal:

export FLASK_APP=app.py

export FLASK_ENV=development



With these commands being run, you can type: flask run , into the terminal and the application should run on your browser. To check the database simply type: sqlite3 schedule.db , into the terminal. After this is done you should type the command: .schema , to see what the tables in the database look like. If nothing happens when this command is run then that means that the tables were not saved appropriately; fortunately, there is a fix for this. You can re-create the tables within the terminal by typing the following commands:

CREATE TABLE option1 (id INTEGER, date DATETIME, weekday TEXT, can_schedule BIT, appointment BIT, charge BIT, holliday BIT, PRIMARY KEY(id));

CREATE TABLE option2 (id INTEGER, date DATETIME, weekday TEXT, can_schedule BIT, appointment BIT, charge BIT, holliday BIT, PRIMARY KEY(id));



Once this is done you schould be able to type: .schema , and see both of these tables appear in the terminal. You can then exit out of the sql database by using Ctrl-C and run flask again by typing: flask run

Alternatively, you can use this url to go to the application through a hosted server: http://pedromanon.pythonanywhere.com/

Once the application is running using flask or by using the url you should be able to see a navbar at the very top with 5 inputs (client name, membership type, location, weekends only, and date) and a submit button. The only inputs absolutely required for the button to submit are the membership type input and the date input. All other inputs have defaults, but considering this application will create a pdf that will require a clients signature, its best that all inputs are filled for filing reasons. Once all of the inputs are submitted the algorithm in the application will run and display a personalized pdf based on the input parameters. The pdf will display the clients name, the store location, and the mebership type of the client at the very top; below it there will be two calendars for an entire year after the purchase date outlining when the client will be charged, scheduled for an appointment, or both. The calendar on the left will be run using an algorithm that charges the client once per month on the same day every month as well as schedules them for an appointment on that same day every month (if the store is open, otherwise it schedules them for the nearest possible alternative day) and it schedules them for an appointment in between charges; the day for that changes depending on how many days pass between charges. The calendar on the right charges the client every 28 days starting from the day of the mebership purchase; and schedules the client every 14 days. In the 13th and 26th appointment, the charge day changes to 14 days later so as to give the client two extra appointments per year with no charge. The option 1 calendar adjusts to whether or not the client wants to be scheduled in the weekends only; if the client chooses this option then all appointments will be on Saturday. The option 2 calendar does not adjust to the request to schedule the client in the weekends only because it must remain rigid in the structure that the client is charged every 28 days and scheduled every 14 days. If the client wants to be schedeuled only in the weekends in option 2, then they should buy their membership on a Saturday.

I should make clear that this application is meant for employees of the Lash Lounge to be able to use, so they will be the ones responsible for using this application; not customers.

The pdf that is output to the screen has a navigation bar that allows you do do things like, minimize or maximize the pdf, rotate the pdf, download the pdf, print the pdf, and other options. This application was made with the intention that the pdf would be printed and given to the client for their signature and later filing.