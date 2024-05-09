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
    