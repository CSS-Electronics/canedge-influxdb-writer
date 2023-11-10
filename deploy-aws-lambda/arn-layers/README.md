# Build ARN layers for multiple regions 
1. Install [Docker Desktop for Windows](https://hub.docker.com/editions/community/docker-ce-desktop-windows)
2. Open the Docker Desktop and wait until it's running
3. Open your command prompt and run `docker pull public.ecr.aws/sam/build-python3.9`
4. Install the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
5. Cofigure your AWS CLI via `aws configure --profile [your_profile_name]`, providing your admin credentials and output type `json`
6. In Docker go to 'Settings/Resources/File Sharing', then add your new folder
7. Update the information in `python build_layers.py` to fit your requirements (note that you can only create layers for regions that are accessible via your AWS account)
8. Once updated, start by running the script with `run_req_build = True` to create the dependencies via Docker and the script 
9. Next, zip the resulting `python/` folder into a zip file named accordingly to match the name in the script 
10. Set `run_req_build = False` and run the script again to start publishing the layers to the regions you've specified