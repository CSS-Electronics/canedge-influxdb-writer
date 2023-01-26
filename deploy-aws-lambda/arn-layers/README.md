# Build ARN layers for multiple regions 
1. Install [Docker Desktop for Windows](https://hub.docker.com/editions/community/docker-ce-desktop-windows)
2. Open the Docker Desktop and wait until it's running
3. Open your command prompt and run `docker pull public.ecr.aws/sam/build-python3.9`
4. Install the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
5. Cofigure your AWS CLI via `aws configure`, providing your admin credentials and output type `json`
6. In Docker go to 'Settings/Resources/File Sharing', then add your new folder
7. Run the file via `python build_layers.py` 
8. If you've already built the zip file with dependencies, you can set this step to False in the code 

Note: Some regions are not currently supported.