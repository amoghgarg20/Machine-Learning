import regex
import pandas as pd
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
from datetime import *
import datetime as dt
from matplotlib.ticker import MaxNLocator
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

def date_time(s):
    pattern = '^([0-9]+)(\/)([0-9]+)(\/)([0-9]+), ([0-9]+):([0-9]+)[ ]?(AM|PM|am|pm)? -'
    result = regex.match(pattern, s)
    if result:
        return True
    return False

def find_author(s):
    s = s.split(":")
    if len(s)==2:
        return True
    else:
        return False

def getDatapoint(line):
    splitline = line.split(' - ')
    dateTime = splitline[0]
    date, time = dateTime.split(", ")
    message = " ".join(splitline[1:])
    if find_author(message):
        splitmessage = message.split(": ")
        author = splitmessage[0]
        message = " ".join(splitmessage[1:])
    else:
        author= None
    return date, time, author, message

#Performing Operations
data = []
conversation =input("Enter the file name(Eg. abc.txt):")
#Ordering Data
with open(conversation, encoding="utf-8") as fp:
    fp.readline()    #1st Message is not needed(Encryption Message)
    messageBuffer = []
    date, time, author = None, None, None
    while True:
        line = fp.readline()
        if not line:
            break
        line = line.strip()
        if date_time(line):
            if len(messageBuffer) > 0:
                data.append([date, time, author, ' '.join(messageBuffer)])
            messageBuffer.clear()
            date, time, author, message = getDatapoint(line)
            messageBuffer.append(message)
        else:
            messageBuffer.append(line)

df = pd.DataFrame(data, columns=["Date", 'Time', 'Author', 'Message'])
df['Date'] = pd.to_datetime(df['Date'])
print("Particiapnts:",df.Author.unique())
#URL Operations
URLPATTERN = r'(https?://\S+)'
df['urlcount'] = df.Message.apply(lambda x: regex.findall(URLPATTERN, x)).str.len()
links = np.sum(df.urlcount)
print("Total Number of messages:",df.shape[0])
print("Total number of media messages:",df[df["Message"]=='<Media omitted>'].shape[0])
print("Total number of links shared:",links)

media_messages_df = df[df['Message'] == '<Media omitted>']
messages_df = df.drop(media_messages_df.index)
messages_df['Letter_Count'] = messages_df['Message'].apply(lambda s : len(s))
messages_df['Word_Count'] = messages_df['Message'].apply(lambda s : len(s.split(' ')))
messages_df["MessageCount"]=1

l = df.Author.unique()
bar_graph=[]
l1=[]
l2=[]
for i in range(1,len(l)):
    # Filtering out messages of particular user
    req_df= messages_df[messages_df["Author"] == l[i]]
    # req_df will contain messages of only one particular user
    print(f'Stats of {l[i]} -')
    # shape will print number of rows which indirectly means the number of messages
    print('Text Messages Sent:', req_df.shape[0])
    #Word_Count contains of total words in one message. Sum of all words/ Total Messages will yield words per message
    words_per_message = (np.sum(req_df['Word_Count']))/req_df.shape[0]
    print('Average Words per message:', words_per_message)
    #media conists of media messages
    media = media_messages_df[media_messages_df['Author'] == l[i]].shape[0]
    print('Media Messages Sent:', media)
    #links consist of total links
    links = sum(req_df["urlcount"])   
    print('Links Sent:', links)
    print('\n')
    bar_graph.append(len(req_df)+media)
    l1.append(len(req_df))
    l2.append(media)
    

fig = plt.figure(figsize = (10, 5))
plt.bar(l[1:],bar_graph,color ='maroon',width =0.2)
plt.xlabel("Members")
plt.ylabel("Number of Messages")
plt.title("Activities of Participants")
plt.show()

  
X_axis = np.arange(len(l[1:]))
  
plt.bar(X_axis - 0.2, l1, 0.4, label = 'Text Messages')
plt.bar(X_axis + 0.2, l2, 0.4, label = 'Media Messages')
  
plt.xticks(X_axis, l[1:])
plt.xlabel("Members")
plt.ylabel("Number of Messages")
plt.title("Activity of Participants")
plt.legend()
plt.show()

#Word-Cloud
text = " ".join(review for review in messages_df.Message)
print ("There are {} words in all the messages.".format(len(text)))
stopwords = set(STOPWORDS)
# Generate a word cloud image
wordcloud = WordCloud(stopwords=stopwords, background_color="black").generate(text)
# Display the generated image:
# the matplotlib way:
plt.figure( figsize=(10,5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()

#Most Active Hours
lst = []
for i in df['Time'] :
    out_time = datetime.strftime(datetime.strptime(i,"%I:%M %p"),"%H:%M")
    lst.append(out_time)
df['24H_Time'] = lst
df['Hours'] = df['24H_Time'].apply(lambda x : x.split(':')[0])

plt.figure(figsize=(8,5))
std_time = df['Hours'].value_counts().head(5)
s_T = std_time.plot.bar()
s_T.yaxis.set_major_locator(MaxNLocator(integer=True))  #Converting y axis data to integer
plt.xlabel('Hours (24-Hour Clock)',fontdict={'fontsize': 12,'fontweight': 10})
plt.ylabel('No. of messages',fontdict={'fontsize': 12,'fontweight': 10})
plt.title('Most active hour of day.',fontdict={'fontsize': 18,'fontweight': 8})
plt.show()


