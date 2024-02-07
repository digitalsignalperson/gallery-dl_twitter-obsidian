import json

paths = {
'flat_clean' : '/home/andy/git/gallery-dl/dump_00-bookmarks.json',
'flat_raw' : '/home/andy/git/gallery-dl/raw00-bookmarks.json',
'expand_raw' : '/home/andy/git/gallery-dl/raw01-bookmarks.json',
}

log_path_expand = '/home/andy/git/gallery-dl/log_dump_01-bookmarks.txt'
with open(log_path_expand) as f:
    log_data_expand = f.read()

log_path_flat = '/home/andy/git/gallery-dl/log_dump_00-bookmarks.txt'
with open(log_path_flat) as f:
    log_data_flat = f.read()



json_data = {}
for k, v in paths.items():
    with open(v) as f:
        if 'raw' in k:
            datas = f.read()
            data = json.loads(datas.replace("\n][\n", ",\n"))
        else:
            data = json.load(f)
    json_data[k] = data


for tweet in json_data['flat_clean'][:20]:
    if tweet[0] == 2:
        data = tweet[1]
    else:
        continue

    tweet_id = str(data['tweet_id'])
    user_name = data['user']['name']
    content = data['content']
    content_short = content.replace('\n', '\\n')[:50]
    print(f'{tweet_id} {content_short:050} {user_name}')



debug_by_tweet = []
i = None
messages = []
for line in log_data_expand.splitlines():
    if line.startswith('[twitter][debug]'):
        if '69420_' in line:
            if i != None:
                debug_by_tweet.append(';'.join(messages))
                messages = []
            i = line.partition('69420_')[-1]
        else:
            if i != None:
                message = line.partition(' ')[-1]
                messages.append(message)
if len(messages):
    debug_by_tweet.append(';'.join(messages))


for i, tweet in enumerate(json_data['expand_raw'][:40]):
    cid = tweet['legacy']['conversation_id_str']
    # same as legacy/{id_str,self_thread/id_str} ?

    favorited = tweet['legacy']['favorited']
    content = tweet['legacy']['full_text']
    tweet_id = tweet['rest_id']
    user_id = tweet['core']['user_results']['result']['rest_id']
    user_name = tweet['core']['user_results']['result']['legacy']['screen_name']

    is_retweet = "retweeted_status_id_str" in tweet['legacy']
    is_quoted = "quoted_by_id_str" in tweet['legacy']
    
    if "in_reply_to_user_id_str" in tweet['legacy']:
        is_reply = tweet['legacy']['user_id_str'] != tweet['legacy']["in_reply_to_user_id_str"]
    else:
        is_reply = False

    reply_to = tweet['legacy'].get('in_reply_to_status_id_str')
    reply_to_screen = tweet['legacy'].get('in_reply_to_screen_name')

    quoted_by = tweet['legacy'].get('quoted_by')

    content_short = content.replace('\n', '\\n')[:50]
    print(f'{i:02} {tweet_id} {content_short:050} {user_name:15} {cid} {favorited:1} {is_retweet:1} {is_quoted:1} {is_reply:1} {reply_to} {debug_by_tweet[i]}')



# new test data
v = '/home/andy/git/gallery-dl/dump_x-bookmarks.json'
v = '/home/andy/git/gallery-dl/dump_custom-flat.json'
v = '/home/andy/git/gallery-dl/dump_custom-expand.json'

with open(v) as f:
    jsondata = json.load(f)

for tweet in jsondata:
    if tweet[0] == 2:
        data = tweet[1]
    else:
        continue

    tweet_id = str(data['tweet_id'])
    user_name = data['user']['name']
    content = data['content']
    content_short = content.replace('\n', '\\n')[:50]

    cid = data["_favorite_cid"]
    expanded = data["_favorite_expanded"]
    index = data["_favorite_index"]
    number= data["_favorite_number"]
    quoted = data["_favorite_quoted"]
    filename = data["_filename"]

    print(f'{filename} {content_short:050} {user_name:15} {cid}')

