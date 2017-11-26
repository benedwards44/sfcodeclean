# Salesforce Code Clean

This application scans all the (non-packaged) Apex Classes in your Org to builds a table of where each property, variable and method is used. Useful for cleaning up unused code.

## API

This tool can also be accessed with API to run a job, scan your Org and retrieve the results in JSON format.

### Step 1 - Start Job

Send a POST request to start your job.
```
https://sfcodeclean.herokuapp.com/api/job/
{
    "accessToken": "VALID_SALESFORCE_ACCESS_TOKEN",
    "instanceUrl": "SALESFORCE_ORG_URL"
}
```

You will then receive an ID for the job. You use this ID to check the status of your job, and ultimately retrieve the results.
```
{
    "id": "6210f461-0a4b-437d-be39-f885d6f3e543",
    "success": true
}
```


### Step 2 - Check Progress

The API runs asynchronously, as jobs can take some time to run depending on the size of your code base. You need to check the status of the job, and when complete you can get your results.
Send a GET request:
```
https://sfcodeclean.herokuapp.com/api/job/status/JOB_ID (eg. https://sfcodeclean.herokuapp.com/api/job/status/6210f461-0a4b-437d-be39-f885d6f3e543)
{
    "status": "Processing",
    "done": false,
    "success": false,
    "error": null
}
```

The done and success variables will help you determine when your job is complete, and if it's successful.


### Step 3 - Get Results

And finally, you can get your results. Send a GET request:
```
https://sfcodeclean.herokuapp.com/api/job/JOB_ID (eg. https://sfcodeclean.herokuapp.com/api/job/6210f461-0a4b-437d-be39-f885d6f3e543)
[
    {
        "DatabaseId": 123 // The app database Id of the class. Not really relevant for the API
        "ApexClassId" "01pb0000004oZiU" // The Salesforce Apex Class Id
        "Name": "AccountController" // The Salesforce name of the class
        "SymbolTable": {
            // The full SymbolTable for the class
        }
    }
]
```
