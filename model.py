import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle
import os

os.makedirs("model", exist_ok=True)

data = {
    "area":[1000,1200,1500,800,950,1100,1700],
    "bedrooms":[2,3,3,1,2,2,4],
    "bathrooms":[2,2,3,1,2,2,3],
    "parking":[1,1,2,0,1,1,2],
    "age":[5,3,2,10,6,4,1],
    "price":[3875000,5000000,6500000,2500000,3600000,4200000,8500000]
}

df = pd.DataFrame(data)
X = df.drop("price", axis=1)
y = df["price"]

model = LinearRegression()
model.fit(X,y)

pickle.dump(model, open("model/house_model.pkl","wb"))
print("Model trained & saved!")