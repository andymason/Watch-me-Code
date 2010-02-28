"""
This file is part of Watch Me Code.

Watch Me Code is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Watch Me Code is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Watch Me Code. If not, see<http://www.gnu.org/licenses/>.
"""
import os, cgi, bitly
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson

# Create DB model
class Project(db.Model):
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)

# Homepage. Nothing special here
class MainPage(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'views/homepage.html')
        self.response.out.write(template.render(path, False))

# Create DB object and generate URL Links for user
class CreateProject(webapp.RequestHandler):
    def post(self):
        # Create DB object
        project = Project()
        project.content = ''
        key = project.put()
        
        # Shorten URLs
        bitly_api = bitly.Api(login='andymason', apikey='R_75e57334a1c672299f77ad6cbc11d653')
        edit_url = bitly_api.shorten('http://' + self.request.host + '/editor?project=' + str(key))
        view_url = bitly_api.shorten('http://' + self.request.host + '/observer?project=' + str(key))
        
        # Get DB Object ID
        page_vals = {
            'project_id': key,
            'edit_url': edit_url,
            'view_url': view_url
        }
        
        # Render page
        path = os.path.join(os.path.dirname(__file__), 'views/create_project.html')
        self.response.out.write(template.render(path, page_vals))
        
    # Send user's to homepage if they directly access the create page
    def get(self):
        self.redirect('/')

class ViewProject(webapp.RequestHandler):
    def get(self):
        # Check that we get a project ID
        if not self.request.get('project'):
            # No project code was suplied, show error messgae
            DisplayError('Missing project code', 400, self, 'http')
            return
        
        # Get the passed in project ID
        project_id = cgi.escape(self.request.get('project'))
        
        # Connect to the DB and get the project
        try:
            project = Project.get(project_id)
        except:
            # Oops! There's not matching DB record
            DisplayError('Not found in the Database', 400, self, 'http')
            return
        
        # Good, it's a valid record. Lets display it
        page_vals = {
            'key': project_id,
            'content': project.content
        }
        
        # Render the page
        path = os.path.join(os.path.dirname(__file__), 'views/observer.html')
        self.response.out.write(template.render(path, page_vals))

class EditProject(webapp.RequestHandler):
    def get(self):
        # Check that we get a project ID
        if not self.request.get('project'):
            # No project code was suplied, show error messgae
            DisplayError('Missing project code', 400, self, 'http')
            return
        
        # Get the passed in project ID
        project_id = cgi.escape(self.request.get('project'))
        
        # Connect to the DB and get the project and
        # check if a record matching that key
        try:
            project = Project.get(project_id)
        except:
            # Oops! There's not matching DB record
            DisplayError('Project not found in database', 400, self, 'http')
            return
        
        # Good, it's a valid record. Lets display it
        page_vals = {
            'key': project_id,
            'content': project.content
        }
        
        # Render the page
        path = os.path.join(os.path.dirname(__file__), 'views/editor.html')
        self.response.out.write(template.render(path, page_vals))

class SaveProject(webapp.RequestHandler):
    def post(self):
        # Check that we get a project ID
        if not self.request.get('key'):
            DisplayError('Key or content paramater error', 400, self, 'json')
            return
        
        # Get the passed in project ID
        key = cgi.escape(self.request.get('key'))
        content = cgi.escape(self.request.get('content'))
        
        # Connect to the DB and get the project
        # check if a record matching that key
        try:
            project = Project.get(key)
        except:
            # Oops! There's not matching DB record
            DisplayError('Sorry, no project was found', 400, self, 'json')
            return
        
        # Good, it's a valid record. Lets save the changes
        project.content = content
        project.put()
        
        # Build response vals
        response_vals = {
            'success': 'Saved data successfully'
        }
        
        # Output json response
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(simplejson.dumps(response_vals))

class GetContent(webapp.RequestHandler):
    def get(self):
        # Check if a key was passed
        if not self.request.get('key'):
            DisplayError('No key was passed', 400, self, 'json')
            return
        
        # Now lets get the DB record
        key = cgi.escape(self.request.get('key'))
        
        # Lets try and get the record
        try:
            project = Project.get(key)
        except:
            # Oops! There's not matching DB record
            DisplayError('No record found for that key', 400, self, 'json')
            return
        
        # Get the content value from the record
        content = project.content
        
        # Build response vals
        response_vals = {
            'content': content
        }
        
        # Send json response with project content
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(simplejson.dumps(response_vals)) 

# Output Error Messages
def DisplayError(msg, error_code, obj, format):
    # Create the error message
    page_vals = {
        'error': msg
    }
    
    # Set the response code
    obj.response.clear()
    obj.response.set_status(error_code)
    
    # Output error message in specified format
    if format == 'json':
        obj.response.headers['Content-Type'] = 'application/json'
        obj.response.out.write(simplejson.dumps(page_vals))
    else:
        path = os.path.join(os.path.dirname(__file__), 'views/error.html')
        obj.response.out.write(template.render(path, page_vals)) 

# Configure URL routing
application = webapp.WSGIApplication(
                [('/', MainPage),
                ('/create_project', CreateProject),
                ('/view', ViewProject),
                ('/edit', EditProject),
                ('/save', SaveProject),
                ('/get', GetContent)],
                debug=True)

# Run the application
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
