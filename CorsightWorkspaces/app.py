from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import base64
from typing import List
import sys
import full_flow as cs
from pydantic import BaseModel

app = FastAPI()

class CreateWatchlistRequest(BaseModel):
    display_name: str
@app.post("/create_watchlist/")
async def create_watchlist_endpoint(request: CreateWatchlistRequest):
    return cs.create_watchlist(request.display_name)

class DetectFaceRequest(BaseModel):
    base64_img: str
    get_crops: bool = True
@app.post("/detect_face/")
async def detect_face_endpoint(request: DetectFaceRequest):
    return cs.detect_face_return_full_response(request.base64_img)

class AddPOIRequest(BaseModel):
    base64_img: str
    watchlist_id: str
    file_name: str
@app.post("/add_poi/")
async def add_poi_endpoint(request: AddPOIRequest):
    # link to s3 image, key(witch represented the poi)
    return cs.detect_and_add_all_pois_in_image_to_watchlist(request.base64_img, request.watchlist_id, request.file_name)

class SearchPOIRequest(BaseModel):
    base64_img: str
    watchlist_id: str
    min_confidence: int
    max_matches: int

@app.post("/search_poi/")
async def search_poi_endpoint(request: SearchPOIRequest):
    #link to s3 image,
    return cs.search_poi_in_watchlist(request.base64_img, request.watchlist_id, request.min_confidence, request.max_matches)




@app.get("/get_all_pois/")
async def get_all_pois_endpoint(watchlist_id: str):
    return cs.get_all_pois_from_watchlist(watchlist_id)


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

