![asKanton Logo](https://github.com/SAint7579/START_Kanton_VoiceBot/blob/main/asKanton.PNG)

# Automated Chatbot for Help Sector Calls - Canton of St. Gallen

Welcome to our GitHub repository for the project developed by our team for the Start Hack 2024 hackathon! Our project aims to automate the calls made to the help sector of Canton of St. Gallen using an automated voicebot.

## Project Overview

In this project, we have developed an automated voicebot that leverages scraped data from the website, designed to handle incoming calls completely over the phone, aiming to reduce the need for human intervention in answering user queries, with the ability to redirect calls to relevant departments. 

## Features

- **Automated Call Handling**: The chatbot is capable of handling incoming calls from users without requiring human assistance.
- **Scraped Data Training**: We trained the chatbot using data from the website to provide accurate and up-to-date information to users.
- **Reduced Human Effort**: By automating call handling, our project aims to significantly reduce the amount of time, money, and effort required for humans to answer calls from users.
- **Directing to Relevant Departments**: The chatbot is programmed to answer straightforward user questions, while queries that cannot be answered are directed to the relevant department.

## Usage

Our codebase is available in this repository, along with instructions for deploying and running the automated chatbot system. Feel free to explore the code and adapt it to your own projects.

#### To deploy local python webhook:
```cd Twillio Deployment/local-python``` <br>
```flask run &```<br>
```ngrok http 5000```
Use this webhook with your twilio deployment.

#### To run streamlit playground:
```streamlit run app.py```

#### To deploy serverless:
```cd Twillio Deployment/serverless-twilio```<br>
```twilio serverless:deploy```<br>
```twilio phone-numbers:update –voice-url={transcribe URL}```

## Contributing

We welcome contributions from the community to improve and extend the functionality of our automated chatbot project.

Thank you for your interest in our project! 
