# BizCardX-extracting_business-card-data-OCR

## Introduction

BizCardX is a Python application that allows users to upload an image of a business card and extract relevant information from it using Optical Character Recognition (OCR). This information includes the company name, card holder name, designation, mobile number, email address, website URL, area, city and pin code. The extracted information can be displayed in the application's graphical user interface (GUI), and users can save it to a database. Users can also view , update, and delete the stored data through the Streamlit UI.

## Table of Contents

    1.	Key Technologies
    2.	Installation
    3.	Usage
    4.	Workflow

## Key Technologies
    •	Python scripting
    •	easyOCR
    •	Streamlit
    •	Postgresql

## Installation

    To run this project, you will need to install the following packages
        pip install streamlit
        pip install psycopg2
        pip install streamlit_option_menu
        pip install pandas
        pip install easyocr
        pip install cv2
        pip install re
         
    
## Usage

   To use this project, kindly follow the following steps:
   
        1.	Clone the repository: git clone https://github.com/Theressac/Streamlit-app-youtube-data
        2.	Install the required packages
        3.	Run the Streamlit app: streamlit run bizcard.py
        4.	Access the app in your browser at http://localhost:8501

## Workflow

        •	Image Upload: Users upload a business card image through the Streamlit interface.
        •	Text Extraction: EasyOCR performs OCR on the uploaded image, extracting relevant text.
        •	Data Classification: Regular expressions are applied for classification, enhancing data accuracy.
        •	Database Interaction: The classified data is stored in a PostgreSQL database for easy retrieval and management.
        •	User Interaction: Users can effortlessly view, update, and delete the stored data through the Streamlit interface.

## Author

    @Theressac
  
