# Code Samples
This repo contains a mix of sample code, done in different languages:

1.  SimpleLogger.py - A python logger that allows me to log to the console, a file, or both. File logging is capped to prevent filling up the file system.

2.  PyTorchPerformanceTester.py - Some python code to test the performance of various ways to do matrix multiplications in pytorch (popular library used for developing and training deep learning models).

3.  sqlexpr - Contains files needed to create a Docker image with SQL Server Express 2022 for Windows, minus the SQL Server Express 2022 install kit itself.  Microsoft discontinued support for its Windows-based SQL Server Express container back in 2016. But I have a little personal project testing some features in the Windows version of SQL Server Express. 

NOTE:  Microsoft says I can make the instructions to build such a container public and build images for my use, but I can't make the image itself publicly available.  You can get the SQL Server Express 2022 install kit from this URL (https://www.microsoft.com/en-us/download/details.aspx?id=104781).  You will need to run the installer and select "Download Media", selecting "Express Core (266 MB) SQL Server Engine Only", which will retrieve SQLEXPR_x64_ENU.exe.  After downloading, SQLEXPR_x64_ENU.exe, you will then need to run it and extract the files for the kit and exit installation. The extracted files are what needs to be in the SQLEXPR2022.zip file referenced in the CICD pipeline.  This is because the SQLEXPR_x64_ENU.exe doesn't appear to let me extract the files non-interactively from the headless Windows Server Core container.

I created a simple CICD pipeline (technically just CI, since I'm not deploying in this example).  I set the pipeline to be manually triggered only, though I left the code (commented out) to automatically build on commit to main and upon pull request to main.  The pipeline grabs the SQL Server Express 2022 kit from a private Azure Storage account and uses those bits to build the container.  I omit adding a security scan step, since I don't know if you plan on running this code but have your own security provider (SonarQube, Checkmarx, etc).

I use OIDC to authenticate against Azure using the following secrets stored in my Github: 

    `${{ secrets.SOFTWARE_DOWNLOADS_AZURE_CLIENT_ID }}` 
    `${{ secrets.SOFTWARE_DOWNLOADS_AZURE_TENANT_ID }}` 
    `${{ secrets.SOFTWARE_DOWNLOADS_AZURE_SUBSCRIPTION_ID }}` 
    `${{ secrets.SOFTWARE_DOWNLOADS_AZURE_STORAGE_ACCOUNT }}` 

In Azure, to authorize Github access via OIDC, you will need to use the Azure CLI to:
1. Create an application (az ad app create)
2. Create a service principal (az ad sp create)
3. Create a federated credential (az ad app federated-credential create).  Note that the subject claim needs to exactly match what github sends, as wildcards are not currently (as of 2025-10-01) supported in Azure!  See:  https://learn.microsoft.com/en-ie/answers/questions/2073829/azure-github-action-federated-identity-login-issue
4. Assign a Storage Blob Data Reader role (az role assignment create)

NOTE:  The issue with lack of wildcard support appears to be specific to Azure.  AWS does appear to support wildcards.  See: https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws


