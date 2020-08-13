import docker
import argparse
import os
import sys
import subprocess
from getpass import getpass
from docker.errors import APIError, TLSParameterError

client = docker.from_env()
fname = os.getcwd()

    # METHODS
def execute_deploy(a,u,r,t,f):
    os.system("ibmcloud fn action create "+a+" --docker "+u+"/"+r+":"+t+" "+f+" --web true")

def username_input():
    print("Enter your Docker Hub username: ")
    username = input()
    return username

def username_password():
    passwd = getpass("Password: ")
    return passwd

def login_dockerhub(username, passwd):
    try:
        client.login(username=username, password=passwd)
        logged_in = True
        print("Logged in to DockerHub")
    except APIError as e:
        if(e.status_code == 401):
            print("Wrong Credentials. Please try again...")
            logged_in = False
    
    return logged_in




class ADEPS(object):
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='''ADEPS helps you deploy your serverless actions with third party packages.

                Ensure that your serverless function and Dockerfile is located in the same directory before running the deploy command.''',
            usage='''adeps command [<args>]
            The available commands are listed below:



            deploy     Deploy a function to a serverless environment'''

            )
        parser.add_argument('command', help="Enter a command to run")
        args = parser.parse_args(sys.argv[1:2])
        #if class does not have inputed commmand as an attribute
        if not hasattr(self, args.command):
            print('Command not recognized')
            parser.print_help()
            exit(1)
        #call the attribute in the class
        getattr(self, args.command)()

    def deploy(self):
        #Enter parser arguments
        parser = argparse.ArgumentParser(
            description="ADEPS helps you deploy your serverless actions with third party packages. " \
                "Ensure that your serverless function and Dockerfile is located in the same directory before running the deploy command."
            )
        parser.add_argument('-d', '--dockerhub', required=True, help="Enter true if you want to create a new docker hub. If true, please provide a reponame and tagname")
        #parser.add_argument('--dockerfile', metavar="", required=True, type=argparse.FileType('r'), help="Please provide the path to your Dockerfile")
        parser.add_argument('-r', '--reponame', required=True, help="Please provide your Dockerhub Repo Name. If you don't have a repo, provide a name for the repo that will be created else enter the name of your desired repo")
        parser.add_argument('-t', '--tagname', required=True, help="Please provide a tagname for your repo. If you don't have a tagname, provide a name for the tag that will be created.")
        parser.add_argument('-f', '--functionfile', required=True, help="please provide your serverless action")
        parser.add_argument('-a', '--actionname', required=True, help="please provide a name for your serverless action that will be deployed")
        args = parser.parse_args(sys.argv[2:])

         #assign arguments to variables
        reponame = args.reponame
        tagname = args.tagname
        functionfile = args.functionfile
        dockerhub = args.dockerhub
        actionname = args.actionname
        

        # If user provides false credentials, loop until user is logged in
        user_logged_in = False
        while user_logged_in == False:
            username = username_input()
            passwd = username_password()
            user_logged_in = login_dockerhub(username, passwd)

        path = os.path.dirname(fname+'/Dockerfile')
        print("Building Docker Image...")

        #if user wants to create a docker image and push to dockerhub repo
        if(dockerhub == "true"):
            try:
                client.images.build(path=path, dockerfile="Dockerfile", gzip=False, tag=username+"/"+reponame+":"+tagname)
            except NameError:
                print("Error Occured")

            #push docker image to docker hub
            #list = client.images.list()
            for line in client.images.push(username+"/"+reponame+":"+tagname, stream=True, decode=True):
                print(line)

            print("Docker image sucessfully published")


        #deploy to ibm function

        try:
            execute_deploy(actionname, username, reponame, tagname, functionfile)
        except subprocess.CalledProcessError as e:
            print(e)



#function entrypoint
if __name__ == "__main__":
    ADEPS()