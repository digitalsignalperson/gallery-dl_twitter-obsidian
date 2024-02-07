import os
import json
import re
from collections import Counter, defaultdict

def get_files_sorted(root_dir):
    all_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            modification_time = os.path.getmtime(file_path)
            all_files.append((modification_time, file_path))

    all_files = [x[1] for x in sorted(all_files)]
    return all_files


base_dir = os.path.expanduser('~/twitter/bookmarks3')
download_dir = os.path.join(base_dir, "twitter")
vault_dir = os.path.join(base_dir, "vault")
attach_dir = os.path.join(vault_dir, "z_attachments")  # currently unused
tweet_dir = os.path.join(vault_dir, "tweets")
users_dir = os.path.join(vault_dir, "users")
tags_dir =  os.path.join(vault_dir, "tags")
tags_canvas_dir =  os.path.join(vault_dir, "tags_canvas")

following_dir = os.path.expanduser('~/twitter/following/twitter/')

os.makedirs(vault_dir, exist_ok=True)
os.makedirs(attach_dir, exist_ok=True)
os.makedirs(tweet_dir, exist_ok=True)
os.makedirs(users_dir, exist_ok=True)
os.makedirs(tags_dir, exist_ok=True)
os.makedirs(tags_canvas_dir, exist_ok=True)

"""
TODO obsidian settings
- enable random note
- tag pane? not useful yet
- css snippet for nice embed
- disable inline title 
"""



def touch_mentions(data):
    if 'mentions' in data and False:
        for mention in data['mentions']:
            
            # Touch user file
            mention_name = mention['name']
            with open(os.path.join(users_dir, mention_name + '.md'), 'a'):
                pass


def get_modified_content(data):
    content = data['content']
    
    if 'mentions' in data:
        names = [mention['name'] for mention in data['mentions']]
        content = replace_with_links(content, names, '@')
    
    if 'hashtags' in data:
        content = replace_with_links(content, data['hashtags'], '#', 'tags/')

    return content


def replace_with_links(content, items, symbol='#', path=None):
    path = path or ''
    modified_content = ''
    # content_parts = re.split(r'(\s+)', content) # split by whitespace
    # content_parts = re.split(r'(\W+)', content) # split by whitespace & punctuation
    content_parts = re.split('(' + symbol + ')', content)
    items_out = []
    check_next = False
    for c in content_parts:
        d = c
        if check_next:
            check_next = False
            c = symbol + c
            d = c
            more_parts = re.split(r'(\W+)', c)
            # sometimes hashtag has trailing punctuation
            x = more_parts[2]
            if symbol ==  '#':
                more_parts[2]= f'[[{path}{x.lower()}|➡️]] #{x}' # You lose the tag if it's in a link
                more_parts = more_parts[2:]
            else:
                if path:
                    more_parts[2] = f'[[{path}{x}|{x}]]'
                else:
                    more_parts[2] = f'[[{x}]]'
            
            if x not in items_out:
                items_out.append(x)
            
            d = ''.join(more_parts)

        elif c == symbol:
            check_next = True
            d = ''
        
        modified_content += d
    
    items_out_lower = [x.lower() for x in items_out] # TODO this is so dumb
    for x in items:
        if x not in items_out and x.lower() not in items_out_lower:
            raise
    
    if not items:
        for i in items_out:
            items.append(i)
    
    return modified_content


def get_md_content(data):
    tweet_id = str(data['tweet_id'])
    user_name = data['user']['name']
    content = data['content']
    content_modified = get_modified_content(data)

    media_startswith = json_path.partition(f'metadata')[0] + tweet_id
    media_paths = [x for x in all_files if x.startswith(media_startswith)]

    md_content = content_modified + '\n\n'

    for media_path in media_paths:
        if media_path.endswith('.mp4'):
            md_content += f'<video src="file://{media_path}" controls loop muted autoplay></video>\n\n'
        else:
            md_content += f'![](file://{media_path})\n\n'
    
    return md_content


def quoted(content):
    lines = []
    for line in content.rstrip().splitlines():
        lines.append('> ' + line)
    return '\n'.join(lines) + '\n\n'


def touch_author(data):
    pass
    # user_name = data['user']['name']
    # with open(os.path.join(users_dir, user_name + '.md'), 'a'):
    #     pass


def get_title(data):
    user_name = data['user']['name']
    url = get_url(data)
    return f"[{data['date']}]({url}) [[{user_name}]]"


def get_url(data):
    user_name = data['user']['name']
    tweet_id = str(data['tweet_id'])
    return f"https://twitter.com/{user_name}/status/{tweet_id}"




following_files = get_files_sorted(following_dir)
following_json = [x for x in following_files if x.endswith('.json')]
following_media = [x for x in following_files if not x.endswith('.json')]

# following = {}

following_path = os.path.join(vault_dir, 'following.md')

# clear tag files
for f in os.listdir(tags_dir):
    os.remove(os.path.join(tags_dir, f))

with open(following_path, 'w') as f:
    f.write('\n') # annoying cursor position thing if first line not blank
    f.write('| Name | Description | Followers | Following |\n')
    f.write('| --- | --- | --- | --- |\n')

for f_json in following_json:
    screen_name = f_json.rsplit('/', 3)[1]
    f_dir = os.path.join(following_dir, screen_name)
    f_media = [x for x in following_media if x.startswith(f_dir)]

    profile_path = None
    banner_path = None
    for x in f_media:
        name = os.path.split(x)[-1]
        if name.startswith('1_None'):
            profile_path = x
        elif name.startswith('2_None'):
            banner_path = x

    with open(f_json) as f:
        data = json.load(f)
    
    # data['author'] == data['user']

    user = data['user']
    description = user.get('description', '')
    description_md = replace_with_links(description, [], '@')
    user_tags = []
    description_md = replace_with_links(description_md, user_tags, '#', 'tags/')

    user_md_lines = [
    f"# {user['nick']}" + (' ✅' if user['verified'] else ''),
    f"## @{screen_name}",
    '',
    f"*{description_md}*",
    '',
    f'🗓️ Joined {user["date"][:7]}',
    f'Location: {user["location"]}',
    f'Followers: {user["followers_count"]}, following: {user["friends_count"]}',
    f'Number of tweets: {user["statuses_count"]}, likes: {user["favourites_count"]}, media: {user["media_count"]}',
    ]
    if profile_path:
        # pics += [f'![|128](file://{profile_path})']
        avatar = f'<img src="file://{profile_path}" style="float:left; width:128px; padding-right: 10px;">'
        user_md_lines[3] = avatar + user_md_lines[3]
    if banner_path:
        # ![|0x192] works in other modes, but not canvas
        #banner = f'![](file://{banner_path})'
        banner = f'<img src="file://{banner_path}" style="max-height:192px;">'
        user_md_lines.insert(1, banner)

    user_md = '\n'.join(user_md_lines)

    user_path = os.path.join(users_dir, screen_name + '.md')
    with open(user_path, 'w') as f:
        f.write(user_md)
        f.write('\n\n')
        f.write('# Bookmarks\n')
        f.write('\n')


    with open(following_path, 'a') as f:
        # f.write(f'- [[{screen_name}|@{screen_name}]] {user_md_lines[0][2:]}\n')
        # desc = description.replace('\n', ' ')
        # f.write(f'    - {desc}\n')
        # # stuff = ' | '.join(user_md_lines[-4:][::-1])
        # stuff = user_md_lines[-2]
        # f.write(f'    - {stuff}\n')

        name = f'{user_md_lines[0][2:]} [[{screen_name}|@{screen_name}]]'
        name = name.replace('|', '\|')
        desc = description.replace('\n', ' ').replace('|', '\|')
        a = user["followers_count"]
        b = user["friends_count"]
        f.write(f'| {name} | {desc} | {a} | {b} |\n')

        # Maybe this should be a cool card embed by reference

    for tag in user_tags:
        # use tag.lower() in filename because there is no unique casing
        tag_md = os.path.join(tags_dir, tag.lower() + '.md')
        exists = os.path.exists(tag_md)
        with open(tag_md, 'a') as f:
            if not exists:
                canvas_file = tag.lower() + '.canvas'
                f.write('\n') # annoying cursor position thing if first line not blank
                f.write(f'[[{canvas_file}]]\n\n')
                f.write('# Following\n\n')
                f.write('| Name | Description | Followers | Following |\n')
                f.write('| --- | --- | --- | --- |\n')
                    
            name = f'{user_md_lines[0][2:]} [[{screen_name}|@{screen_name}]]'
            name = name.replace('|', '\|')
            desc = description.replace('\n', ' ').replace('|', '\|')
            a = user["followers_count"]
            b = user["friends_count"]
            f.write(f'| {name} | {desc} | {a} | {b} |\n')

for t in os.listdir(tags_dir):
    tag_md = os.path.join(tags_dir, t)
    with open(tag_md, 'a') as f:
        f.write('\n')
        f.write('# Bookmarks\n\n')


bookmarks_path = os.path.join(vault_dir, 'bookmarks.md')
try:
    os.remove(bookmarks_path)  # this will be re-written with append mode
except:
    pass

# Get list of files sorted by date modified - the order of our bookmarks
all_files = get_files_sorted(download_dir)
all_json = [x for x in all_files if x.endswith('.json')]

# I used to use the date modified beacuse the unmodified gallery_dl didn't give the needed data
all_json = sorted(all_json, key=lambda x: os.path.split(x)[-1])

json_names = [os.path.split(x)[-1] for x in all_json]
assert all([x == y for x, y in zip(sorted(json_names), json_names)])
# This assert fails if you don't do the above sort. The sort by date modified somehow is not the expected order

tweet_to_json_path = {json_name.split('_')[-2] : json_path for json_name, json_path in zip(json_names, all_json)}


# TODO this sucks
cid_authors = defaultdict(set)

def write_markdown(json_path, last_user=None, sep=True):
    with open(json_path) as f:
        data = json.load(f)
    
    tweet_id = str(data['tweet_id'])
    user_name = data['user']['name']
    content = data['content']
    md_content = get_md_content(data)
    title = get_title(data)
    url = get_url(data)

    # title = title + ' ' + url

    # Touch mentions
    touch_mentions(data)
    # Touch tweet author
    touch_author(data)

    cid = data['_favorite_cid']
    fav_expanded = data['_favorite_expanded']
    fav_index = data['_favorite_index']
    fav_number = data['_favorite_number']
    is_quote = data['_favorite_quoted']

    global cid_authors
    cid_authors[cid].add(user_name)
    
    md_path = os.path.join(tweet_dir, cid + '.md')
    
    filename = data['_filename']
    content_short = content.replace('\n', '\\n')[:50]
    print(f'{filename} {content_short:050} {user_name:15}')

    with open(md_path, 'a') as f:
        if is_quote:
            f.write('> \n')
            f.write('> > [!quote] ' + title + '\n')
            # f.write('> ' + url + '\n')
            f.write('> > \n')
            f.write(quoted(quoted(md_content).rstrip()).rstrip() + '\n')
        else:
            if sep:
                f.write('\n')
            #     f.write('---\n')
            # else:
            #     f.write('\n')
            if user_name != last_user:
                f.write('> [!quote] ' + title + '\n')
                f.write('> \n')
                last_user = user_name
            else:
                # f.write('> [!quote] \n') # It says "Quote". :\
                f.write('> [!quote] ' + title + '\n')  # TODO?
                f.write('> \n')
            
            f.write(quoted(md_content).rstrip() + '\n')
            f.write('> \n')
    
    return last_user


convo_to_tweets = defaultdict(set)
convo_to_favorites = defaultdict(set)
for filename in json_names:
    fav_number, fav_index, is_quote, is_expanded, tweet_id, cid = filename[:-5].split('_')
    if not int(is_quote):
        convo_to_tweets[cid].add(tweet_id)

        if int(fav_index) == 0:
            convo_to_favorites[cid].add(tweet_id)

favs_with_one_tweet = [convo for convo, convo_tweets in convo_to_tweets.items() if len(convo_tweets) == 1]


cid_to_embed_lines = defaultdict(list)
written_files = []
# First pass for first section
for i, json_path in enumerate(all_json):
    json_filename = os.path.split(json_path)[1]
    fav_number, fav_index, is_quote, is_expanded, tweet_id, cid = json_filename[:-5].split('_')

    if int(fav_index) != 0:
        continue
    
    md_path = os.path.join(tweet_dir, cid + '.md')
    sep = True
    # sep = False
    if md_path not in written_files:
        # sep = False
        # Make new markdown file
        with open(md_path, 'w') as f:
            f.write('')
        written_files.append(md_path)

        with open(bookmarks_path, 'a') as f:
            f.write(f'[[{cid}]]\n\n')

    write_markdown(json_path, sep=sep)

    do_bookmark = False
    if len(all_json) > (i + 1):
        next_fav_number, next_fav_index, next_is_quote = os.path.split(all_json[i+1])[1].split('_')[:3]
        if next_fav_number == fav_number and next_is_quote == '1':
            do_bookmark = False
        else:
            do_bookmark = True
    else:
        do_bookmark = True
    
    if do_bookmark:
        with open(md_path, 'a') as f:
            f.write(f'^{fav_number}\n')

        with open(bookmarks_path, 'a') as f:
            line = f'![[{cid}#^{fav_number}|clean]]\n\n'
            f.write(line)
            cid_to_embed_lines[cid].append(line)
            # use this css snippet! https://github.com/SlRvb/Obsidian--ITS-Theme/blob/main/Guide/Embed-Adjustments.md
            # f.write('\n')

# Close off the top section
for md_path in written_files:
    cid = os.path.split(md_path)[1][:-3]
    with open(md_path, 'a') as f:
        # if cid not in favs_with_one_tweet:
        # f.write('\n[[#Conversation|...continue thread]]\n')
        f.write('\n# Conversation\n')
        if cid in favs_with_one_tweet:
            f.write('N/A\n')

# Second pass for conversation section
last_user = None
skip_next_quote = False
convo_to_tweets_written = defaultdict(list)
for json_path in all_json:
    json_filename = os.path.split(json_path)[1]
    fav_number, fav_index, is_quote, is_expanded, tweet_id, cid = json_filename[:-5].split('_')
    
    if cid in favs_with_one_tweet:
        continue

    # TODO don't mix string/int uses
    if int(fav_index) == 0:
        continue
    
    if int(fav_index) == 1:
        sep = False

    md_path = os.path.join(tweet_dir, cid + '.md')
    # if tweet_id == '....................':
    #     break
    
    if skip_next_quote:
        skip_next_quote = False
        if is_quote == '0':
            pass
        else:
            continue
    
    if is_quote == '1':
        write_markdown(json_path)
    elif tweet_id not in convo_to_tweets_written[cid]:
        if int(fav_index) == 1 and tweet_id in convo_to_favorites[cid]:
            # the first expanded tweet was shown above
            with open(md_path, 'a') as f:
                f.write('...continued from above\n\n')
            skip_next_quote = True
        else:
            last_user = write_markdown(json_path, last_user, sep=sep)
            sep = True
        
        convo_to_tweets_written[cid].append(tweet_id)




# Finally, close it off with a notes section
for md_path in written_files:
    with open(md_path, 'a') as f:
        f.write('\n# Notes\n\n')


cid_to_tags = defaultdict(Counter)
tags_to_cid = defaultdict(Counter)
for json_path in all_json:
    with open(json_path) as f:
        data = json.load(f)
    
    cid = data['_favorite_cid']
    if 'hashtags' in data:
        for tag in data['hashtags']:
            cid_to_tags[cid][tag] += 1
            tags_to_cid[tag][cid] += 1



# Make tag files
# TODO missing the users in the table complete based on tags used in bookmarks

for tag in tags_to_cid.keys():
    cids = tags_to_cid[tag].keys()
    # use tag.lower() in filename because there is no unique casing
    tag_md = os.path.join(tags_dir, tag.lower() + '.md')
    exists = os.path.exists(tag_md)
    with open(tag_md, 'a') as f:
        if not exists:
            canvas_file = tag.lower() + '.canvas'
            f.write('\n') # annoying cursor position thing if first line not blank
            f.write(f'[[{canvas_file}]]\n\n')
            f.write('# Bookmarks\n\n')
        for cid in cids:
            cid_tags = cid_to_tags[cid].keys()
            line = f'[[{cid}]]'
            for author in cid_authors[cid]:
                line += f' [[{author}|@{author}]]'
            for cid_tag in cid_tags:
                line += f' [[tags/{cid_tag}]]'
            line += '\n'
            f.write(line)
            # f.write(f'![[{cid}|clean]]\n\n')  # wish I could say "embed until section X"
            for line in cid_to_embed_lines[cid]:
                f.write(line)

for cid, authors in cid_authors.items():
    for author in authors:
        cid_tags = cid_to_tags[cid].keys()
        line = f'[[{cid}]]'
        for author in cid_authors[cid]:
            line += f' [[{author}|@{author}]]'
        for cid_tag in cid_tags:
            line += f' [[tags/{cid_tag}]]'
        line += '\n'
        
        user_md = os.path.join(users_dir, author + '.md')
        if os.path.exists(user_md):
            with open(user_md, 'a') as f:
                f.write(line)
                # f.write(f'![[{cid}|clean]]\n\n')  # wish I could say "embed until section X"
                for line in cid_to_embed_lines[cid]:
                    f.write(line)


group_to_tags = {}
tag_to_group = {}
group_index = 0
def get_name():
    global group_index
    group = '%03i' % group_index
    group_index += 1
    return group

for cid in cid_to_tags:
    tags = [x.lower() for x in cid_to_tags[cid].keys()]

    if len(group_to_tags) == 0:
        # start the first group
        group = get_name()
        group_to_tags[group] = []
        for tag in tags:
            tag_to_group[tag] = group
            group_to_tags[group].append(tag)
    else:
        # only create a new group if none of the tags are in an existing group
        group = None
        for tag in tags:
            if tag in tag_to_group:
                if group and tag_to_group[tag] != group:
                    # merge this group
                    g = tag_to_group[tag]
                    print(f'merging {g} into {group}')
                    merge_tags = group_to_tags.pop(g)
                    group_to_tags[group] += merge_tags
                    for t in merge_tags:
                        tag_to_group[t] = group
                    
                else:
                    group = tag_to_group[tag]
        
        if group:
            for tag in tags:
                if tag not in tag_to_group:
                    tag_to_group[tag] = group
                else:
                    assert tag_to_group[tag] == group
                
                if tag not in group_to_tags[group]:
                    group_to_tags[group].append(tag)

        else:
            group = get_name()
            group_to_tags[group] = []
            for tag in tags:
                tag_to_group[tag] = group
                group_to_tags[group].append(tag)

print("group_to_name = {")
for k, v in group_to_tags.items():
    print(f"    '{k}': '', #" + ' '.join(v))
print('}')

group_to_name = {
    '000': 'cg/frameworks/engines/godot', #godotengine godot4
    '005': 'cg/frameworks/web/threejs', #threejs
    '006': 'art/plotter', #drawingmachines plotterart penplotter
    '007': 'art/generative', #genuary13 genuary genuary2023
    '008': 'art', #つぶやきglsl define fxhash p5js webgl shader creativecoding glsl genart generative wip shadertoy duck fluidsimulation realtime generativeart プログラミング ジェネラティブアート plottertwitter failure sdf digitalart art loop satisfying unrealengine gamedev indiedev unity madewithunity dailycoding mathematics sdfs raymarching procedural desmos mathart animation gfx gpu editor hlsl opengl metal directx demoscene axidraw openframeworks inktober inktober2020 pulsar landscapeart processing processingtutorial video javascript luluxxx objkt hicetnunc nftcommunity pokemon pex ai generated illustration nft diffusion tezos cleannft nftcollection monogrid wccchallenge cryptoart nftartist beautiful blender3d tinycode landscape trees generativedesign computerart
    
    # 2024-02: Stripped the rest of my tags.  This is enough for an example
}



import secrets

def create_node(path, x, y, width, height):
    return {"id": secrets.token_hex(8), "x": x, "y": y, "width": width, "height": height, "type": "file", "file": path}

def tile_nodes(paths, width, height, columns, x_space, y_space):
    nodes = []
    for i, path in enumerate(paths):
        column = i % columns
        row = i // columns
        x = column * (width + x_space)
        y = row * (height + y_space)
        node = create_node(path, x, y, width, height)
        nodes.append(node)
    return nodes

for f in [x for x in get_files_sorted(vault_dir) if x.endswith('.canvas')]:
    os.remove(f)

rows = 4
cols = 8
width = 400
height = 600
x_space = 10
y_space = 40

"""
at 400x600, 5x7 (rows, cols)
    can only really see 3x7 zooomed in clearly
    zoomed out, could fit 2x more columns, but super laggy if I try
    obsidian is slow to load it

maybe 3x10?
"""

canvas_paths_all = ['tweets/' + os.path.split(m)[1] for m in written_files]

canvas_paths_chunked = [[]]
for p in canvas_paths_all:
    if len(canvas_paths_chunked[-1]) < rows * cols:
        canvas_paths_chunked[-1].append(p)
    else:
        canvas_paths_chunked.append([p])

for i, paths in enumerate(canvas_paths_chunked):
    nodes = tile_nodes(paths, width, height, cols, x_space, y_space)
    canvas_data = {"nodes" : nodes, "edges" : []}

    canvas_file = os.path.join(vault_dir, f'Bookmarks canvas {i:02}.canvas')
    with open(canvas_file, "w") as f:
        json.dump(canvas_data, f)


rows = 4
cols = 4
width = 400
height = 600
x_space = 10
y_space = 40



# Make tag canvases
for f in os.listdir(tags_canvas_dir):
    os.remove(os.path.join(tags_canvas_dir, f))

for tag in tags_to_cid.keys():
    cids = tags_to_cid[tag].keys()
    # use tag.lower() in filename because there is no unique casing
    
    paths = ['tweets/' + cid + '.md' for cid in cids]
    
    nodes = tile_nodes(paths, width, height, cols, x_space, y_space)
    canvas_data = {"nodes" : nodes, "edges" : []}

    canvas_file = os.path.join(tags_canvas_dir, tag.lower() + '.canvas')
    with open(canvas_file, "w") as f:
        json.dump(canvas_data, f)


rows = 4
cols = 4
width = 400
height = 600
x_space = 10
y_space = 40


cids = []
for tag in group_to_tags['008']:
    for cid in tags_to_cid[tag].keys():
        if cid not in cids:
            cids.append(cid)


paths = ['tweets/' + cid + '.md' for cid in cids]

nodes = tile_nodes(paths, width, height, cols, x_space, y_space)
canvas_data = {"nodes" : nodes, "edges" : []}

canvas_file = os.path.join(tags_canvas_dir, '008.canvas')
with open(canvas_file, "w") as f:
    json.dump(canvas_data, f)


# Make follower canvas
rows = 4
cols = 6
width = 400
height = 1000
x_space = 10
y_space = 40
canvas_paths_all = ['users/' + f_json.rsplit('/', 3)[1] + '.md' for f_json in following_json]

canvas_paths_chunked = [[]]
for p in canvas_paths_all:
    if len(canvas_paths_chunked[-1]) < rows * cols:
        canvas_paths_chunked[-1].append(p)
    else:
        canvas_paths_chunked.append([p])

for i, paths in enumerate(canvas_paths_chunked):
    nodes = tile_nodes(paths, width, height, cols, x_space, y_space)
    canvas_data = {"nodes" : nodes, "edges" : []}

    canvas_file = os.path.join(vault_dir, f'following canvas {i:02}.canvas')
    with open(canvas_file, "w") as f:
        json.dump(canvas_data, f)

