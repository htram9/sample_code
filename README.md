# Sample code
This repo contains a mix of sample code, done in different languages:

1.  SimpleLogger.py - A python logger that allows me to log to the console, a file, or both. File logging is capped to prevent filling up the file system.

2.  PyTorchPerformanceTester.py - Some python code to test the performance of various ways to do matrix multiplications in pytorch (popular library used for developing and training deep learning models).

3.  sqlexpr - Creates a Docker image with SQL Server Express 2022 for Windows.  Microsoft discontinued support for its Windows-based SQL Server Express container back in 2016. But I have a little personal project testing some features in the Windows version of SQL Server Express.

Microsoft says I can make the instructions to build such a container public and build images for my use, but I can't make the image itself publicly available.

I created a simple CICD pipeline (technically just CI, since I'm not deploying in this example).  I set the pipeline to be manually triggered only, though I left the code (commented out).  It grabs the SQL Server Express 2022 kit from a private Azure Storage account, and uses those bits to build the container.  I omit adding a security scan step, since I don't know if you plan on running this code but have your own security provider.

I use OIDC to authenticate azure using the following secrets stored in my Github:
    ${{ secrets.SOFTWARE_DOWNLOADS_AZURE_CLIENT_ID }}
    ${{ secrets.SOFTWARE_DOWNLOADS_AZURE_TENANT_ID }}
    ${{ secrets.SOFTWARE_DOWNLOADS_AZURE_SUBSCRIPTION_ID }}
    ${{ secrets.SOFTWARE_DOWNLOADS_AZURE_STORAGE_ACCOUNT }}

In Azure, to authorize Github access via OIDC, you will need to use the Azure CLI to:
3.1. Create an application (az ad app create)
3.2. Create a service principal (az ad sp create)
3.3. Create a federated credential (az ad app federated-credential create).  Note that the subject claim needs to exactly match what github sends as wildcards are not currently supported!
3.4. Assign a Storage Blob Data Reader role (az role assignment create)


