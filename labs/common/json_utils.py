import re

def get_end_indicator(start_indicator):
    if start_indicator == '[':
        return ']'
    
    if start_indicator == '{':
        return '}'
    
    if start_indicator == '"':
        return '"'
    
    return ''

# extract json text
def extract_json_text(text):
    # start indicator {, [, "
    start_indicator = re.compile(r'[\{\[\"]')
    start_index = text.find(start_indicator.search(text).group()) if start_indicator.search(text) else 0
    
    start_char = text[start_index]
    end_char = get_end_indicator(start_char)
    
    if end_char == '':
        return text
    
    end_index = text.rfind(end_char)
    
    return text[start_index:end_index + 1]

def clean_json_text(text):
    json_content = extract_json_text(text)
    
    # trim the text
    json_content = json_content.strip()
    
    # get content ```json content ```
    json_content = json_content.replace('```json\n', '').replace('```', '')
    
    # remove any // comments to the end of the line
    json_content = re.sub(r'//.*', '', json_content)
    
    return json_content

if __name__ == '__main__':
    print(clean_json_text('any text { "a": 1 } any text'))
    
    print(clean_json_text('any text [{ "a": 1 }] any text'))
    
    print(clean_json_text('any text "a": 1 } any text'))
    
    print(clean_json_text('any text "a": 1 " any text'))
    
    print(clean_json_text('any text "a": 1 " any text'))
    
    print(clean_json_text("1"))
    
    print(clean_json_text('any text'))
    
    print(clean_json_text('```json\n{ "a": 1 }\n```'))
    
    print(clean_json_text('```json\n{ "a": 1 }\n``` any text'))
    
    print(clean_json_text('any text ```json\n{ "a": 1 }\n``` any text'))
    
    print(clean_json_text('{ "a": 1 // comment \n}'))
    
    
    print(clean_json_text("""```json
{
  "General": {
    "name": "HUYNH THANH LONG",
    "born": "05/02/1996",
    "position": "MOBILE DEVELOPER"
  },
  "Contacts": {
    "phone": "0352761705",
    "email": "thanhlong9704@gmail.com",
    "LinkedIn": "https://www.facebook.com/ht.long.96",
    "GitHub": null
  },
  "EmploymentHistory": [
    {
      "companyName": "Công ty công nghệ ICEO",
      "type": "Full-time",
      "startDate": "12/9/2022",
      "endDate": "22/4/2024",
      "position": "Mobile Developer",
      "responsibility": "Developed various mobile applications using React Native and related technologies. Projects include WhiteG (dating app), CallU (video call app), an ecosystem system utilizing ChatGPT's API, and Gamification apps (Gamifa Biz and Gamifa Social).",
      "level": 2
    },
    {
      "companyName": "Công ty TNHH công nghệ Vihat",
      "type": "Full-time",
      "startDate": "10/8/2020",
      "endDate": "15/8/2022",
      "position": "Mobile Developer",
      "responsibility": "Developed Widdy, a mobile app for selling automobiles, motorcycles, and insurance products using React Native and various technologies.",
      "level": 2
    },
    {
      "companyName": "Công ty CP và đầu tư truyền thông Nam Hương",
      "type": "Full-time",
      "startDate": "9/2/2020",
      "endDate": "7/2020",
      "position": "Mobile Developer",
      "responsibility": "Participated in building WSERVICE, an e-commerce app, using React Native and ContextAPI.",
      "level": 1
    },
    {
      "companyName": "Social App",
      "type": "Project",
      "startDate": "9/11/2019",
      "endDate": "2/2020",
      "position": "Mobile Developer",
      "responsibility": "Participated in building Booking event, a social app for seeking human resources for events, using React Native, Redux, and Redux-Saga.",
      "level": 1
    },
    {
      "companyName": "E-commerce app",
      "type": "Project",
      "startDate": "9/12/2019",
      "endDate": "1/2020",
      "position": "Mobile Developer",
      "responsibility": "Participated in building Babyh, an e-commerce app for mom and baby products, using React Native, Redux, and Redux-Thunk.",
      "level": 1
    },
    {
      "companyName": "Crypto wallet",
      "type": "Project",
      "startDate": "30/10/2019",
      "endDate": "15/12/2019",
      "position": "Mobile Developer",
      "responsibility": "Participated in building Onespay (version 1), a crypto wallet app with features for managing Bitcoin, Etherium, and other coins, using React Native, Hooks, Redux, and Redux Saga.",
      "level": 1
    },
    {
      "companyName": "Money loan app",
      "type": "Project",
      "startDate": "20/10/2019",
      "endDate": "11/11/2019",
      "position": "Mobile Developer",
      "responsibility": "Participated in building Easyvtn, a money loan app, using React Native, Hooks, and ContextAPI.",
      "level": 1
    }
  ]
}
``` 
"""))