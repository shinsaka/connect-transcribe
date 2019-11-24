# about
- Catch event s3 put
    - Submit transcribe job if s3 file is wav>
    - Post slack messages from transcribed contexts.

# deploy

## prepare
- Setting Amazon Connect with "Data storage -> Call recordings".
- Install Serverless Framework

```
npm install serverless -g
```

- Create `serverless.yml` for your environment.

## deploy

```
pip install -r requirements.txt  -t site-packages/ --upgrade
sls deploy
```
