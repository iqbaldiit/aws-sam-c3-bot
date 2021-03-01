import json
import csv
import re
import boto3
import uuid



def lambda_handler(event, context):
    #user_input=event['currentIntent']['slots']['user_input']
    final_result= answer(event['user_input'])
    # response={
    #     "dialogAction":{
    #         "type":"Close",
    #         "fulfillmentState":"Fulfilled",
    #         "message":{
    #             "contentType":"SSML",
    #             "content":"{}".format(final_result)
    #         }
    #     }
    # }
    return final_result

s3_client=boto3.client('s3') 
dynamodb=boto3.client('dynamodb',region_name='us-east-1')

reserveWords=['a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't",
'it', "it's", 'its', 'itself', "let's", 'me', 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'these', 'they', "they'd", "they'll",
"they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves',"learn","like","want","aws","amazon"]

def answer(user_input):
    insert_user_input=user_input
    #remove special charecter and make a list
    user_input=list(re.sub(r"[^a-zA-Z0-9]"," ",user_input).lower().split())

    #remove stopwords & reserve words for better searching
    user_input=[word for word in user_input if word not in reserveWords] #reserve words

    #remove duplicate elements from user input
    #user_input=dict.fromkeys(user_input)
    user_input=list(set(user_input))

    #read csv file and store information in a list
    # path="assets\docs\AWS_Services.csv"
    # fileReader=csv.reader(open(path))
    # fileHeader=next(fileReader) #seperate file header
    # fileData=[row for row in fileReader] #now this is only the list without header

    csv_file = s3_client.get_object(Bucket= 'mmi-cloud-camp-sam', Key= 'AWS_Services.csv')
    csv_record_list=csv_file['Body'].read().decode('utf-8', errors="replace").split("\n")
    csv_reader=csv.reader(csv_record_list,delimiter=',', quotechar='"')
    csv_header=next(csv_reader)    
    fileData=[row for row in csv_reader] #now this is only the list without header
    no_of_elements=len(fileData)

    #search each item of user   input
    search_result=[]
    for uInput in user_input:
        for r in fileData[0:no_of_elements-1]:
            if uInput in ' '.join([r[0],r[1]]).lower():
                search_result.append(r[0]+"-->"+r[1]+"("+r[3]+")")
    #problem: cant delete duplicate record from this list.

    #search_result=[r for r in fileData if user_input in ' '.join([r[0],r[1]]).lower()]
    search_result=[lst for lst in search_result if lst!=[]]
    search_result="Not matched, try again" if search_result==[] else search_result

    # Insert intent to dynamodb
    add_to_db=dynamodb.put_item(
        TableName='mmi-c3-bot-intent-sam',
        Item={
            'intent-id':{'S':str(uuid.uuid4())},
            'user_intent':{'S':str(insert_user_input)}
        }
    ) 

    return search_result



