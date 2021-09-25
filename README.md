# Splash Awards 2021: SafeShop

## Information
SafeShop is a consumer-to-consumer e-commerce website aimed to remove the number and severity of scams by:
- adding warning and verified symbols on listings scanned by AI
- scanning transactions with AI to decrease fradulent transactions
- storing transaction data using ethereum for security

## Requirements
---
To run this project, you might need:
- python3
- a terminal

## How to use
---
### Setting up the firebase: Part 1
For security reasons, the credentials file needed for the database to work is not included. 
You will need to:
1. Create a new firebase project [https://firebase.google.com/docs/projects/learn-more](https://firebase.google.com/docs/projects/learn-more)
2. Download the firebase configuration file, and save it in the root folder with the name `fbConfig.json` [https://support.google.com/firebase/answer/7015592?hl=en](https://support.google.com/firebase/answer/7015592?hl=en)
3. Add the firebase admin configuration file, and save it in the root folder with the name `fbAdminConfig.json` [https://firebase.google.com/docs/admin/setup](https://firebase.google.com/docs/admin/setup)
4. Go to realtime database in your project, and enable it to run in test mode
5. Go to authentication in your project, and turn on authentication by email and password

**Firebase Warnings: The website is not initialised to start with an empty database, and this may cause it to crash.**
### Setting up the firebase: Part 2

In order to allow the website to function, a few parts of the database has to be manually set up.

The database needs to look similar to the following:
```
listings
    index: integer, beginning from 0 [min. 1 listing needed]
        category: string
        description: string
        id: integer, same as index
        image: link to image file
        name: string
        price: float
        stock: integer
        uid: string (from auth)
        username: string
        verified: bool
ratings
    uid: string (from auth) [needed for all users]
        index: integer
            desc: string
            stars: integer (0 to 5)
            username: string
warnings
    uid: integer [needed for all users]
```
You may refer to `sample-data.json`
### Setting up the firebase: Part 3
After registering, go to authentication to find the uid. *I cannot remember if registering auto sets up the warning and ratings, so manually initialise it if necessary.*
The uid can be used to set up the above info.
### Setting up photo uploading
In `templates/create.html`, an API key is required to allow for the uploading and storage of images.
Please visit [https://dev.filestack.com/login/](https://dev.filestack.com/login/) and get an API key, and insert it into the code in `templates/create.html`
### Setting up the virtual environment
Run the following in the terminal:
```
$ python -m venv venv
$ . venv/bin/activate
```
To deactivate:
```
$ deactivate
```

### Install requirements
Run the following in the terminal:
```
$ pip install -r requirements.txt
```
To install the relevant modules. 
## Running the project
---
In order to run the project, run the following command.
```
$ python app.py
```
Alternatively, you may run:
```
$ flask run
```
## Editing the project
---
To edit the following files, please look for the relevant references
- `app.py` database information: firebase database documentation
- `app.py` authentication information: firebase auth documentation
- `app.py` flask: flask documentation
- `templates/*`: jinja2 documentation
## External resources
---
- Firebase realtime database
- Firebase authentication
- Filestack image uploading
- Flask
- jinja2
## Warnings and important notices
---
Please note that the project is in no way complete, and might not be completed. The following features were not implemented for the sake of prototyping:
- uploading transaction data to ethereum (this was run in a separate javascript file that is not included nor integrated as the security of the code have many issues)
- implementation of artificial intelligence for both listing and transaction scanning
- fully functional user data setup

The code may also not be optimised, nor are the security for the database querying very good.
## Notes of thanks and appreciation
---
Project author: Saw Ze Dong (github: [sawzedong](https://github.com/sawzedong))

My teammates: Zheng Kang and Tristan

Our proposal may be found at: [https://docs.google.com/document/d/1Ifmf7NdQzoiLS5i2eM8fWThtHp66hqVr/edit?usp=sharing&ouid=105820086403864632040&rtpof=true&sd=true](https://docs.google.com/document/d/1Ifmf7NdQzoiLS5i2eM8fWThtHp66hqVr/edit?usp=sharing&ouid=105820086403864632040&rtpof=true&sd=true)

Our slides for the presentation may be found at: [https://docs.google.com/presentation/d/16W-uZnFuEFhl2VT8d3PetmpNF3XC3Rv9ojldL6ckqpk/edit?usp=sharing](https://docs.google.com/presentation/d/16W-uZnFuEFhl2VT8d3PetmpNF3XC3Rv9ojldL6ckqpk/edit?usp=sharing)

Our demo video may be found at: [https://drive.google.com/file/d/1KX3akmXpJD6_JlzzPwYJvZprZzKemEuF/view?usp=sharing](https://drive.google.com/file/d/1KX3akmXpJD6_JlzzPwYJvZprZzKemEuF/view?usp=sharing)
