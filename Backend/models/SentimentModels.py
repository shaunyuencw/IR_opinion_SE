# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import torch
# import torch.nn as nn

# app = FastAPI()


# # Load your model here
# # If you're loading the whole model
# model = torch.load('model.pth')

# model.eval()  # Set the model to evaluation mode


# @app.post("/predict/")
# async def create_item(item: Item):
#     try:
#         # Convert input data to a tensor
#         input_tensor = torch.tensor(item.input, dtype=torch.float32)  # Ensure the dtype matches your model's expected input
#         with torch.no_grad():
#             prediction = model(input_tensor)
#         # You might need to post-process the prediction before sending it back
#         return {"prediction": prediction.tolist()}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))