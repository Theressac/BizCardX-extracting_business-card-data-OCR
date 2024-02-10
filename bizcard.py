# Import all the required librairies
import streamlit as st
import easyocr
import cv2
import numpy as np
import pandas as pd
import re
from streamlit_option_menu import option_menu
import psycopg2
from PIL import Image
import io
import streamlit as st

#Connection with the postgres database
con = psycopg2.connect(host="localhost", user="postgres", password="sa", port=5432, database="BusinessCard")
myCursor = con.cursor()

#Initial parameter settings for streamlit
reader = easyocr.Reader(['en'], gpu = False)
st.set_page_config(page_title="Bizcard", page_icon="",layout="wide", initial_sidebar_state="expanded")
st.title(":blue[BizCardX: Extracting Business Card Data with OCR]")

#This function is mainly used to extract the data using the regular expressions and also check the pattern for each type of data.

def extractdata(data):
    for i in range(len(data)):
        data[i] = data[i].rstrip(' ')
        data[i] = data[i].rstrip(',')
        res = ' '.join(data)
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    website_pattern = r'[www|WWW|Www]+[\.|\s]+[a-zA-Z0-9]+[\.|\][a-zA-Z]+'
    phone_pattern = r'(?:\+)?\d{3}-\d{3}-\d{4}'
    phone_pattern2 = r"(?:\+91[-\s])?(?:\d{4,5}[-\s])?\d{3}[-\s]?\d{4}"
    address_pattern = r'\d+\s[A-Za-z\s,]+'
    pincode_pattern = r'\b\d{6}\b'
    name = designation = company = email = website = primary = secondary = address = pincode = None
    
    #To extract the email address
    try:
        email = re.findall(email_pattern, res)[0]
        res = res.replace(email, '')
    except IndexError:
        email = None

    #To extract the website link
    try:
        website = re.findall(website_pattern, res)[0]
        res = res.replace(website, '')
        website = re.sub('[WWW|www|Www]+ ', 'www.', website)
        #website = website.lower()
    except IndexError:
        webstie = None

    #To extract the phone number
    phone = re.findall(phone_pattern, res)
    if len(phone) == 0:
        phone = re.findall(phone_pattern2, res)
    primary = None
    secondary = None
    if len(phone) > 1:
        primary = phone[0]
        secondary = phone[1]
        for i in range(len(phone)):
            res = res.replace(phone[i], '')
    elif len(phone) == 1:
        primary = phone[0]
        res = res.replace(phone[0], '')

    #To find the pincode    
    try:
        pincode = int(re.findall(pincode_pattern, res)[0])
        res = res.replace(str(pincode), '')
    except:
        pincode = 0

    name = data[0]
    res = res.replace(name, '')
    designation = data[1]
    res = res.replace(designation, '')
    address = ''.join(re.findall(address_pattern, res))
    result = res.replace(address, '')
    company = data[-1]
    res = res.replace(company, '')

    info = [name, designation, company, email, website, primary, secondary, address, pincode, result]
    return (info)
with st.sidebar:
    selected = option_menu(
        menu_title="Menu",  
        options=["Upload","---", "View/Update", "---"],  
        icons=["upload","","search",  ""], 
        menu_icon="person-vcard",  
        default_index=0,  
        styles={"nav-link": {"--hover-color": "brown"}},
        orientation="vertical",
    )

# Extract the data fom the business card ad insert in to the database postgresql
if selected == 'Upload':
    uploaded_file = st.file_uploader("Choose a image file",type=["jpg", "jpeg", "png"])
    if uploaded_file != None:
        image = cv2.imdecode(np.fromstring(uploaded_file.read(), np.uint8), 1)
        col1, col2, col3 = st.columns([2,1,2])
        with col3:
            st.image(image)
        with col1:
            result = reader.readtext(image, detail=0)
            info = extractdata(result)
            name = st.text_input('Name:',info[0])
            desig = st.text_input('Designation:', info[1])
            Com = st.text_input('Company:', info[2])
            mail = st.text_input('Email ID:', info[3])
            url = st.text_input('Website:', info[4])
            m1 = st.text_input('Primary Contact:', info[5])
            m2 = st.text_input('Secondary Contact:', info[6])
            add = st.text_input('Address:', info[7])
            pin = st.number_input('Pincode:', info[8])
            upload_button = st.button("upload")
            if upload_button:
                myCursor.execute(
                    """CREATE TABLE IF NOT EXISTS business_cards (name VARCHAR, designation VARCHAR, company VARCHAR, email VARCHAR, website VARCHAR, primary_no VARCHAR,
                    secondary_no VARCHAR, address VARCHAR, pincode int, image bytea)""")
                query = "INSERT INTO business_cards (name, designation, company, email, website, primary_no, secondary_no, " \
                      "address, pincode, image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = (name, desig, Com, mail, url, m1, m2, add, pin, psycopg2.Binary(image))
                myCursor.execute(query, val)
                con.commit()
                st.success('The contact details have been successfully inserted into the database')

#View, update and delete options will be provided based on the selected name
elif selected == 'View/Update':
    col1, col2, col3 = st.columns([2,2,4])
    with col1:
        myCursor.execute('select distinct name from business_cards')
        y = myCursor.fetchall()
        contact = [x[0] for x in y]
        contact.sort()
        selected_contact = st.selectbox('Name',contact)
    with col2:
        mode_list = ['','View','Update','Delete']
        selected_mode = st.selectbox('Mode',mode_list,index = 0)

    #View the full card details of the selected business card
    if selected_mode == 'View':
        col5,col6 = st.columns(2)
        with col5:
            myCursor.execute(f"select name, designation, company, email, website, primary_no, secondary_no, "
                         f"address, pincode from business_cards where name = '{selected_contact}'")
            y = myCursor.fetchall()
            st.table(pd.Series(y[0],index=['Name', 'Designation', 'Company', 'Email ID', 'Website', 'Primary Contact', 'Secondary Contact', 'Address', 'Pincode'],name='Card Info'))

    #Update the contact details based on the selected name in the database
    elif selected_mode == 'Update':
        myCursor.execute(f"select name, designation, company, email, website, primary_no, secondary_no, "
                     f"address, pincode from business_cards where name = '{selected_contact}'")
        info = myCursor.fetchone()
        col5, col6 = st.columns(2)
        with col5:
            name = st.text_input('Name:', info[0])
            desig = st.text_input('Designation:', info[1])
            Com = st.text_input('Company:', info[2])
            mail = st.text_input('Email ID:', info[3])
            url = st.text_input('Website:', info[4])
            m1 = st.text_input('Primary Contact:', info[5])
            m2 = st.text_input('Secondary Contact:', info[6])
            add = st.text_input('Address:', info[7])
            pin = st.number_input('Pincode:', info[8])
        updat_button = st.button("Update")
        if updat_button:
            query = f"update business_cards set name = %s, designation = %s, company = %s, email = %s, website = %s, " \
                    f"primary_no = %s, secondary_no = %s, address = %s, pincode = %s where name = '{selected_contact}'"
            val = (name, desig, Com, mail, url, m1, m2, add, pin)
            myCursor.execute(query, val)
            con.commit()
            st.success('The contact details have been successfully updated in the database')

    #Delete the selected contact details fom the database
    elif selected_mode == 'Delete':
        st.markdown(
            f'__<p style="text-align:left; font-size: 20px; color: #FAA026">You are trying to remove {selected_contact} '
            f'contact from database.</P>__',
            unsafe_allow_html=True)
        confirm = st.button('Confirm')
        if confirm:
            query = f"DELETE FROM business_cards where name = '{selected_contact}'"
            myCursor.execute(query)
            con.commit()
            st.success('The contact details have been successfully removed from the database')

