# Request Image Frames

Request image frames based on depth_min and depth_max

## Deployed on Cloud Server:

https://request-image-frame.onrender.com/docs#/

![Screenshot 2023-12-27 at 4 52 42 pm](https://github.com/alpeshkumar9/request_image_frames/assets/8064993/2dd770fc-9eca-4dec-9a75-3c74c54b013d)

## Setup the application locally

1. Clone this repository to local machine.

   `git clone <repository-url>`<br/>
   `cd <repository-name>`

   Replace `<repository-url>` with the actual URL of the Git repository and <repository-name> with the name of the directory where the repository is cloned.

2. Install Dependencies

- Run `python -m venv venv` to create a virtual environment
- Run `source venv/bin/activate` on mac <strong>or</strong> `.\venv\Scripts\activate` on windows to activate the virtual environment:
- Run `pip install -r requirements.txt` to install the dependencies
- Rename `env.txt` to `.env` to setup the environment.

## Run the tests (Optional)

Before starting the server, if you want to run tests to ensure that everything is working as expected.

- Run `pytest -v` to run all the test cases.

## Run the application

1. Without Docker

- Run `python main.py` to start the application
- Open your web browser and navigate to http://0.0.0.0:4080/docs or http://localhost:4080/docs to access the application interactive API.

2. With Docker

- Run `docker-compose up --build -d` to start the application
- Open your web browser and navigate to http://0.0.0.0:4080/docs or http://localhost:4080/docs to access the application interactive API.
