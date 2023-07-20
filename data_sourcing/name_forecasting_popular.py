
import pandas as pd
from statsmodels.tsa.arima_model import ARIMA
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
import numpy as np

# Load the dataset
df = pd.read_csv('output.csv')

# Calculating total count for each name to use as weights for sampling
name_weights = df.groupby("Name")["Count"].sum()

# Take the top 10K most popular names
top_names = list(name_weights.sample(1000).index)

# Filter the original dataframe to only include the top names
df_sample = df[df["Name"].isin(top_names)]

# Filter names that have at least a 40 year history
#df_sample = df_sample.groupby("Name").filter(lambda x: x['Year'].max() - x['Year'].min() >= 40)

# Sort the data by Year
df_sample.sort_values('Year', inplace=True)

# Initialize lists to store the predictions and actual values
predictions = []
actuals = []

# Iterate over each unique name
for name in df_sample['Name'].unique():
    # Get data for the current name
    data = df_sample[df_sample['Name'] == name]
    
    # Ensure there are at least 40 years of data for this name
    if len(data['Count'].values) >= 40:
        # Train an ARIMA model on the first 30 years of data and make a 10-year prediction
        try:
            model = ARIMA(data['Count'].values[:30], order=(1,1,0))
            model_fit = model.fit(disp=0)
            prediction = model_fit.forecast(steps=10)[0]
        
            # Store the ARIMA predictions and actual values only if the model successfully fits
            predictions.append(prediction)
            actuals.append(data['Count'].values[30:40])
        except:
            continue  # Skip this name if the ARIMA model fails to fit

# Convert lists to numpy arrays and flatten them
predictions = np.array(predictions).flatten()
actuals = np.array(actuals).flatten()

# Train a Gradient Boosting Regressor on the ARIMA predictions and the actual values
X_train, X_test, y_train, y_test = train_test_split(predictions.reshape(-1, 1), actuals, test_size=0.2, random_state=42)
gbr = GradientBoostingRegressor()
gbr.fit(X_train, y_train)

# Score the Gradient Boosting model
score = gbr.score(X_test, y_test)
print('Score:', score)

# Predict the future popularity for the top names using the trained Gradient Boosting model
future_popularity = gbr.predict(predictions.reshape(-1, 1))

# Save the future popularity predictions to a csv file
future_df = pd.DataFrame({'Name': df_sample['Name'].unique(), 'FuturePopularity': future_popularity})
future_df.to_csv('/future_popularity.csv', index=False)
