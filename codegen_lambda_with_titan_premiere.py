import boto3
import botocore.config
import json
from datetime import datetime

def generate_code_using_bedrock(message:str, language:str) -> str:
  
  prompt_text = f"""Act like you are a smart code generator who writes optimized code along with some test cases based on the defined Input Query.
  Please follow below instructions while responding:
  Instructions:
  - Output Code in code blocks with appropriate backticks
  - Use {language} as your coding language
  - Use various optimization techniques making sure you output the most optimized code
  - Provide atleast 3 test cases and test them with the generated code to show the output
  
  Input Query:
  {message}
  
  """
  
  body = {
    "inputText": prompt_text,
    "textGenerationConfig" : {
        "maxTokenCount": 1024,
        "temperature": 0.1,
        "topP": 0.9,
        "stopSequences": []
    }
  }
  
  try:
    bedrock = boto3.client("bedrock-runtime", region_name="us-east-1", config = botocore.config.Config(read_timeout=300, retries = {'max_attempts':3}))
    response = bedrock.invoke_model(body=json.dumps(body), modelId = "amazon.titan-text-premier-v1:0")
    response_content = response.get('body').read().decode('utf-8')
    resposne_data = json.loads(response_content)
    code = resposne_data["results"][0]["outputText"]
    #print(code)
    return code
    
  except Exception as e:
    print(f"Error generating the code : {e}")
    return ""
    
    
def save_code_to_s3_bucket(code, s3_bucket, s3_key):
  s3 = boto3.client('s3')
  try:
    s3.put_object(Bucket = s3_bucket, Key = s3_key, Body = code)
    print("Code saved to S3")
  except Exception as e:
    print("Error when saving code to s3")
    
    
def lambda_handler(event, context):
  event = json.loads(event['body'])
  message = event['message']
  langauge = event['key']
  print(message, langauge)
  
  generated_code = generate_code_using_bedrock(message, langauge)
  
  
  if generated_code:
    current_time = datetime.now().strftime('%H%M%S')
    s3_key = f'code-output/{current_time}.txt'
    s3_bucket = 'bedrock-bucket-sk'
    
    save_code_to_s3_bucket(generated_code, s3_bucket, s3_key)
    return {
      'statusCode':200,
      'body': json.dumps('Code generation complete')
    }
    
  else:
    print("No code was generated")
    return {
      'statusCode':500,
      'body': json.dumps('Error while generating code')
    }
  
