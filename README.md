# Catalog Application Project

This README provides the instructions to the Catalog application project for Udacity Full Stack Web Developer Nanodegree course.



## How The App Works
The application operates as a catalog tool for users to store and share data. Practical uses for this application include knowledge sharing platforms (e.g. Quora, Wikipedia, or Reddit) as well as messageboards and forums for discussion topics. The example used in the course was for restaurant menu items; whilst the example used in this project is for sports categories and gear.

This application allows public users to freely reference and read the information shared on the platform; whilst signed-in users will be able to add, edit and delete their own posts. A Google account will be needed to sign in to this application; using OAuth 2.0 security platform.

User will also be able to review the data using JSON links provided in the Usage section.



## Data structure
There are 4 sets of data in this application.


**Dataset #1: Catalog:**
For this project we only allow 1 instance of Catalog, which houses a set of Categories which in turn house a set of Items within. Think of Catalog like a cluster of restaurants within a shopping mall.

*2 variables (not exposed): 'name', 'description'.*


**Dataset #2: Category (or Subcatalog):**
Subset of Catalog, superset to Item. Think of it like a specific restaurant within that shopping mall.

*8 variables (exposed via JSON): 'category_name', 'category_description', 'datetime_added', 'category_id', 'parent_catalog_id', 'owner_name','owner_email','owner_id'.*


**Dataset #3: Item:**
Subset of Category. This is like a specific menu withinthe specific restaurant within a specific shopping mall.

*9 variables (exposed via JSON): 'item_name', 'item_description', 'datetime_added', 'item_id', 'parent_category', 'parent_id', 'owner_name', 'owner_email', 'owner_id'.*


**Dataset #4: Users:**
The users whom use the above 3 datasets. Think of these as owners of the restaurants who in turn own the menus within them.

*4 variables (not exposed): 'user_name', 'user_email', 'user_picture', 'user_id'.*


## Setup:
1. Download the files from GitHub repository.


2. Set up your Google ID credentials for OAuth2.0. You will need the following setup:

    a. Create a new Web Application on Console.developers.google.com. 

    b. Name the app, and set Authorized Javascript origins to `http://localhost:5000`.
    
    c. Also, add `http://localhost:5000/oauth2callback` to Authorized redirect URIs.
    
    d. Download the client_secrets json file, and rename to client_secrets.json.
    
    e. Place the file in the same folder as the rest of the .py files.
    
    f. Note down your Google ClientID, and copy this value into the /templates/login.html file.
    
    h. Copy and paste the Google ClientID to Line 38 of that file; and then save it.


3. Next, set up your VM environment on your Git Bash platform.

    a. Go to the folder housing the files by typing `cd #name-of-folder`.
    
    b. Set up `vagrant init`, then `vagrant up`, followed by `vagrant ssh`.
    
    c. Once VM is up, go to the vagrant folder by typing `cd /vagrant`.
    
    d. Locate the folder housing the files in the VM environment.


4. Next, set up the database by running `python lotsofcatalog.py`. This creates the catalog.db database with some initial data. 

- Note that if the user wants to be already included in the initial database setup, they can change the dummy user accounts in the lotsofcatalog.py file. The lines to change are 32 and 38 respectively.

- Note that if the user wants to reset the database at any time, they will need to delete the catalog.db file first, before running the `python lotsofcatalog.py` again.


5. Then, run the file by hitting `python main.py`. If all steps are done correctly, you will see the server running.


6. Go to your favourite browser, and go to `http://localhost:5000/catalog/` to start the app.



## Usage:
1. Usage as a public user.

    a. Public users visiting `http://localhost:5000/catalog/` will see all the public data available for viewing. 
    
    b. Data is sorted by Categories on the left column, and Latest Items on the right.
    
    c. By clicking on the name of the Category, they will be able focus on the specified Category to see the associated Items inside.
    
    d. The user will also be able to click on the name of the Item to see the detailed description of the Item.
    
    e. The user will be able to extract the data using JSON by keying in the following links:
- For all Categories:  `http://localhost:5000/catalog/JSON`;

- For all Items in selected Category: `http://localhost:5000/catalog/<string:name_of_category>/JSON`


2. Usage as a signed-in user.

    a. The user will need to click the Login button to be taken to the signin page. 
    
    b. There he/she will need to login using his/her Google ID.
    
    c. Once this is done, he/she will be taken back to the `/catalog` page, but this time more features will be made available.
    
    d. If the signed-in user has previously created Categories and Items before, he/she will be able to edit/delete them now. If there are Categories/Items not created by this user, he/she will NOT be able edit/delete them. If the signed-in user is completely new, they will be taken to the same page but only be allowed to create new Categories and Items. 

    **e. Rules on New Category/Item.**
- New Category: This creates a new category for the signed-in user, where they can then take to create new Items. The Name and Description data is needed.
- New Item: This creates a new Item that needs to be tagged to an existing Category (owned by that specific user). If there is no existing Category, the Item cannot be created. The Name, Description and tagged Category data is needed.
        
    **f. Rules on Edit Category/Item.**
- Edit Category: This allows a signed-in user to edit the Category data that he/she previously created. They will be able to amend the Name and Description data already there. Note that the Name is a unique variable in the Catalog; i.e. no two Categories can have the same name. Also, once a Name of Category is amended, all existing Items tagged to the old Name will now be tagged to the new Name instead. 
- Edit Item: This allows a signed-in user to edit the Item data that he/she previously created. They will be able to amend the Name, Description and associated Category data. Note that the edited Item data needs to be tagged to a Category that exists and is owned by the user.
        
   **g. Rules on Delete Category/Item.**
- Delete Category: This allows the signed-in user to delete the Category he/she previously created. Doing so will also delete all Items tagged to this Category.
- Delete Item: This allows the signed-in user to delete the Item he/she previously created. Doing so will have no effect on the associated Category, other than having 1 less Item tagged.

    h. Hitting the Logout button at any time will lead the signed-in user to become a public user; then taken back to the `/catalog` page (public version). 


3. Security.
Users are prevented from directly keying in `/edit`, `/delete`, `/addItem`, and `/addSubcatalog` to the URLs; as this is insecurely manipulating the data. This applies whether they are public (i.e. non-signed in users), or signed-in users who are not owning those specified Categories/Items. Instead, they will be taken back to the "/login" page.



## Notes, credits and licensing:
It is to be mentioned that some lines in the main.py file do not follow PEP8 compliance; simply because it makes little sense in those situations to wrap the text further. Users should be able to relate to these constraints when examining the code in detail.

Credits go to Lorenzo Brown, the instructor who taught me the "Databases with SQL and Python" Nanodegree course; of which much of the initial code base was also referenced from.

Licensing rights to Google for providing the documentation required to set up Google button for OAuth2.0.
