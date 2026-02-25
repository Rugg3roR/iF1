import os
import pandas as pd
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')

SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

response = supabase.table('f1_results').select('*').execute()

final_df = pd.DataFrame(response.data)



final_df['position'] = pd.to_numeric(final_df['position'], errors='coerce')

final_df['podium'] = (final_df['position'] <= 3).astype(int)

#final_df = final_df.drop(columns=['position'])

features = ['driverId','constructorId','circuitId','year','round', 'event_type']


X = final_df[features]
y = final_df['podium']


X = pd.get_dummies(X, columns=['driverId','constructorId','circuitId','event_type'])


train = final_df['year'] <= 2023

X_train = X[train]
X_test  = X[~train]

y_train = y[train]
y_test  = y[~train]


model = XGBClassifier(n_estimators=100, max_depth=10, random_state=69, eval_metric='logloss')

model.fit(X_train, y_train)

probs = model.predict_proba(X_test)[:, 1]

print(roc_auc_score(y_test, probs))