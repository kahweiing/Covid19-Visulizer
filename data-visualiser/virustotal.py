import hashlib,vt,time

def scan(full_path):
    #count for looping in queue while retrieving result from virustotal
    count = 0
    sha256_hash = hashlib.sha256()

    with open(full_path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    #virustotal api - sign up from virustotal
    #In case client is not working there are another api
    #client = vt.Client("8467397c002fe33f4aef3217f8fbb283368f7701330d4b786292270016becaeb")
    client = vt.Client("5b05c034ef424c1ab180fcfafad4980c211d6452ed3b989c2df7b7dc49924448")

    # This is to upload the file and ensure there is a report in virustotal before proceed to next action
    with open(full_path, "rb") as f:
        print("scan")
        analysis = client.scan_file(f)

    #check the analysis id with virustotal to check whether the id exist
    while True:
        analysis = client.get_object("/analyses/{}", analysis.id)
        #analysis.status will show queued or completed
        print(analysis.status)
        if analysis.status == "completed":
            break
        #program will sleep for awhile before calling virustotal to check id again.
        time.sleep(10)
        count += 1
        #queue 3 times in a row then break the loop of scanning to for smooth scanning
        if count > 2:
            break
    #If program is in queue after breaking will call back scan again this is to prevent virutotal keep looping in queued even if there are result in virustotal database.
    if analysis.status == "queued":
        scan(full_path)
    #Return the result from virustotal reports
    checkresult = client.get_object("/files/" + sha256_hash.hexdigest())
    resultDict = checkresult.last_analysis_stats
    
    #Close the virustotal session after finishing scanning.
    client.close()
    return resultDict
