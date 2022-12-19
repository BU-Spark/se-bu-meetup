# Google Form Script

## Description

Google form sharing link doesn't allow editing, so you'll have to ask client for permission to edit their google form to make a copy.

The script takes in the form information and calls the register endpoint with it to create a new member.

Link to form: https://docs.google.com/forms/d/e/1FAIpQLScd5gWf_-qBYnsuu-DPO1N0LIUff6bYVbGfu-jcgQ6G1ikwkA/viewform?usp=sharing

Link to google sheets: https://docs.google.com/spreadsheets/d/15JCMdNagbJrnLFoqCAn9JBI9ka8dsbOj4i_5o02NuJ8/edit#gid=560292989

## Steps to create google script for form

1. Open form editor
2. Click on the three dots on top right and then click on Script editor
3. Create a script file in editor tab (this file contains your script functions)
4. In the left navigation bar, click on triggers tab and in the triggers page, click on "Add Trigger" on bottom left
5. Hook up function to form and set event type to "On form submit" and save
6. Script should now be executed on form submit
