#! python3
# Reply with subreddit info from subreddit in text body

import praw, bs4, re, os, time, math, datetime

if not os.path.isfile("checked.txt"):
    os.mknod("checked.txt")

# Bot login details
USERNAME = "AutoMobBot"
PASSWORD = "<Password>"
CLIENT_ID = "<ID>"
SECRET = "<SECRET>"

# Subreddit to scan
SUBREDDIT = "needamod"

# Credit left at the end of every bot message
CREDIT = """

---

^I ^am ^a ^bot. [^Feedback](/message/compose?to=%2Fr%2FAutoMobBot&subject=NeedAMod%20Bot&message=) ^| [^Source ^Code](https://github.com/Matthewmob/needamod-bot)"

# Delay between checks (in seconds)
LOOP_DELAY = 900

# Amount of posts to get from /new
GET_POSTS = 5

UA = "/r/NeedAMod Automate Commenter (Update 19) by /u/MatthewMob"

class Reddit(praw.Reddit):
    def login(self, username, password, client_id, secret):
        self.clear_authentication()
        self.set_oauth_app_info(client_id, secret, '')
        r.config.user = username
        r.config.pswd = password
        r.config.grant_type = "password"
        r.config.api_request_delay = 1.0
        r.get_access_information('code')

r = praw.Reddit(UA)
r.login(USERNAME, PASSWORD, CLIENT_ID, SECRET)

def commentSub(sub, post):
    try:
        m = r.get_subreddit(sub, fetch=True)

        d1 = datetime.datetime.utcfromtimestamp(m.created_utc)
        com = "Subreddit Info (/r/{display_name}):\n\n**Age**: " + str((datetime.datetime.now() - d1).days) + " days\n\n**Subscribers**: " + str(m.subscribers) + "\n\n**Current Mods**: " + str(len(m.get_moderators())) + "\n\n**Over 18**: " + str(m.over18) + CREDIT
        
        print("\nCommenting Sub Info")
        print("Commenting on: " + post.id)
        print("Comment: " + com + "\n")

        post.add_comment(com)
    except:
        print("Non-existent subreddit: " + sub)

def commentOffer(post):
    com = "Here are 3 questions to help people who want to recruit you know what you're like:\n\n1. **How Active are you (Eg, hours per day) and what timezone are you in?**\n\n2. **If you see a highly upvoted post, but it doesn't follow the rules, what would you do?**\n\n3. **In your opinion, what is the most important quality a mod can have?**" + CREDIT

    print("\nCommenting Offer to Mod Help")
    print("Commenting on: " + post.id)
    print("Comment: " + com + "\n")

    post.add_comment(com)

def findSub(string):
    return re.findall("\/r\/(.*?)\/", string, re.DOTALL)

def minDif(post):
    d1 = time.mktime((datetime.datetime.utcfromtimestamp(post.created_utc)).timetuple())
    d2 = time.mktime((datetime.datetime.utcnow()).timetuple())

    dif = int(d2-d1)/60
    
    if dif > 5:
        return True
    print("Submission too new\n")
    return False

def postTitle(post):
    getsub = re.findall("\/r\/[a-zA-Z]+", post.title, re.DOTALL)
    if getsub:
        href = getsub[0] + "/"
        getsub = findSub(href)
        commentSub(getsub[0], post)
        return True
    return False

while True:
    with open("checked.txt", "r") as f:
        checked = set(file.read().split())
    print("Checks started\n")
    try:
        submissions = r.get_subreddit(SUBREDDIT).get_new(limit=GET_POSTS)
    except:
        print("Subreddit no found: " + SUBREDDIT)
        break
    for submission in submissions:
        print("Checking " + submission.id + "\n")
        if submission.id not in checked and minDif(submission):
            if submission.link_flair_text != "offer to mod":
                if (submission.is_self and not postTitle(submission) and
                    submission.selftext):
                    soup = bs4.BeautifulSoup(submission.selftext_html, "lxml")
                    a = soup.find_all("a", href=True)
                    if a:
                        href = a[0]["href"] + "/"
                        getsub = findSub(href)
                        if getsub:
                            commentSub(getsub[0], submission)
                elif not submission.is_self:
                    href = submission.url + "/"
                    getsub = re.findall("\/r\/(.*?)\/", href, re.DOTALL)
                    if getsub:
                        commentSub(getsub[0], submission)
                    else:
                        postTitle(submission)
            else:
                commentOffer(submission)

            checked.add(submission.id)

    with open("checked.txt", "w") as f:
        f.write("\n".join(checked))
    print("Checks finished\n")

    time.sleep(LOOP_DELAY)

print("Done...")
input()
