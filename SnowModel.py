import pandas as pd 
import joblib

df = pd.read_csv(r'D:\School\445\AeritaeAutoRoute\Model\incident1.csv')


software = df['assignment_group'] == 'Software'
df_try = df[software]
df =df.append([df_try] , ignore_index=True)

database = df['assignment_group'] == 'Database'
df_try = df[database]
df=df.append([df_try] * 9, ignore_index=True)

network = df['assignment_group'] == 'Network'
df_try = df[network]
df=df.append([df_try] , ignore_index=True)

hardware = df['assignment_group'] == 'Hardware'
df_try = df[hardware]
df=df.append([df_try] , ignore_index=True)

it = df['assignment_group'] == 'IT Securities'
df_try = df[it]
df=df.append([df_try] *4  , ignore_index=True)

it = df['assignment_group'] == 'Service Desk'
df_try = df[it]
df=df.append([df_try], ignore_index=True)



X = df['short_description']
y = df['assignment_group']

#outputs group # 
#print(df['assignment_group'].value_counts())

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = .25, random_state=42)

from sklearn.feature_extraction.text import CountVectorizer
count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(X_train)

from sklearn.feature_extraction.text import TfidfTransformer
tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)

from sklearn.naive_bayes import MultinomialNB
clf = MultinomialNB().fit(X_train_tfidf, y_train)

from sklearn.pipeline import Pipeline
text_clf = Pipeline([('vect', CountVectorizer()),
                    ('tfidf', TfidfTransformer()), 
                    ('clf', MultinomialNB()),])

text_clf.fit(X_train, y_train)

joblib.dump(text_clf, "model.pkl")  #model
X_test1 = ['Help there is a ddos attack on system 2']
predicted = text_clf.predict(X_test1)
prob = text_clf.predict_proba(X_test1)
print(X_test1)
print(str(predicted[0]))
print(prob)
print(text_clf.classes_)
print(max(prob[0]))