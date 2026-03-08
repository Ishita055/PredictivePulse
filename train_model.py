import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os

print("Loading dataset...")
data = pd.read_csv('patient_data.csv')

print("Data Cleaning...")
# Rename column 'C' to 'Gender'
data.rename(columns={'C': 'Gender'}, inplace=True)

# data.drop_duplicates(inplace=True) # Preserving distribution for small classes like NORMAL

print("Encoding categorical variables...")

def clean_string(val):
    if isinstance(val, str):
        return val.strip()
    return val

# Clean up whitespace in strings
for col in data.select_dtypes(include=['object']).columns:
    data[col] = data[col].apply(clean_string)

# Mappings based on requirements
gender_map = {'Male': 0, 'Female': 1}
binary_map = {'No': 0, 'Yes': 1}
age_map = {'18-34': 1, '35-50': 2, '51-64': 3, '65+': 4}
severity_map = {'Mild': 0, 'Moderate': 1, 'Sever': 2} # Note: spelling is 'Sever' in data

# Apply mappings
data['Gender'] = data['Gender'].map(gender_map)
data['Age'] = data['Age'].map(age_map)
data['Severity'] = data['Severity'].map(severity_map)

# Binary features
binary_features = ['History', 'Patient', 'TakeMedication', 'BreathShortness', 
                  'VisualChanges', 'NoseBleeding', 'ControlledDiet']
for feature in binary_features:
    data[feature] = data[feature].map(binary_map)

# Special cases for remaining columns
# Whendiagnoused
when_map = {'<1 Year': 1, '1 - 5 Years': 2, '>5 Years': 3}
data['Whendiagnoused'] = data['Whendiagnoused'].map(when_map)

# Systolic (Midpoints or ordinal)
systolic_map = {'70 - 80': 0, '111 - 120': 1, '121- 130': 2, '130+': 3, '100+': 3} # '100+' high category
data['Systolic'] = data['Systolic'].map(systolic_map)

# Diastolic (Midpoints or ordinal)
diastolic_map = {'70 - 80': 0, '81 - 90': 1, '91 - 100': 2, '100+': 3, '130+': 3}
data['Diastolic'] = data['Diastolic'].map(diastolic_map)

# Target stages: Normal=0, Stage-1=1, Stage-2=2, Crisis=3
# However, the dataset seems to only have Stage-1, Stage-2, and Crisis based on the peek.
# Let's map what we see and handle any missing ones.
target_map = {
    'NORMAL': 0, 
    'HYPERTENSION (Stage-1)': 1, 
    'HYPERTENSION (Stage-2)': 2, 
    'HYPERTENSIVE CRISIS': 3,
    'HYPERTENSIVE CRISI': 3 # Handle typo in data
}
data['Stages'] = data['Stages'].map(target_map)

# Drop any rows with NaN values created by mapping (unseen categories)
data.dropna(inplace=True)

# Separate features and target
X = data.drop('Stages', axis=1)
y = data['Stages']

print("Scaling features...")
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

print("Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.20, stratify=y, random_state=42)

print("Training Gaussian Naive Bayes model...")
model = GaussianNB()
model.fit(X_train, y_train)

print("Evaluating model...")
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy * 100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("Saving model and scaler...")
with open('logreg_model.pkl', 'wb') as f:
    pickle.dump(model, f)
    
with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

print("Done! Files saved mapping structure.")
