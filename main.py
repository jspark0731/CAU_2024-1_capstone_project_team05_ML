import os
import shutil
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Path
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from databases import SessionLocal
from sqlalchemy.orm import Session
import logging

from spleeter.separator import Separator
from basic_pitch.inference import predict_and_save

from CorsConfig import app
from database import engineconn
from models import MLEntity

engine = engineconn()
session = engine.sessionmaker()

class MLDto(BaseModel):
    id: int
    model: str
    instrumentType: str
    fileName: str
    filePath: str
    email: str
    generateSheet: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# # 파일 저장을 위한 임시 디렉터리 생성
# def save_upload_file_tmp(upload_file: UploadFile, path: str) -> None:
#     try:
#         with open(path, "wb") as buffer:
#             shutil.copyfileobj(upload_file.file, buffer)
#     finally:
#         upload_file.file.close()

@app.post("/api/ml/getFile")
async def getDto(mlDto: MLDto):
    id = mlDto.id
    model = mlDto.model
    instrumentType = mlDto.instrumentType
    fileName = mlDto.fileName
    inputFilePath = mlDto.filePath
    email = mlDto.email
    generateSheet = mlDto.generateSheet

    music_entry = db.query(MLEntity).filter(MLEntity.id == mlDto.id).first()

    # spleeter의 결과 path 정의
    spleeterOutputPath = f"/spleeter_output/{email}/{fileName}"
    basicPitchOutputPath = f"/basic_pitch_output/{email}/{fileName}"

    try:
        if not os.path.exists(inputFilePath):
            raise HTTPException(status_code=404, detail="File not found")

        try:
            separator = Separator(f'spleeter:{model}')
            separator.separate_to_file(inputFilePath, spleeterOutputPath)

            if generateSheet == "O":
                instrumentFileName = "others.wav" if mlDto.instrumentType == "guitar" else f"{mlDto.instrumentType}.wav" # instrumentType이 guitar면 others.wav를 사용해야함.
                basicPitchInputPath = os.path.join(spleeterOutputPath, instrumentFileName)

                predict_and_save(
                    [basicPitchInputPath],
                    basicPitchOutputPath,
                    save_midi=True
                )


            else:
                return JSONResponse(status_code=200, content={"message": f"File '{fileName}' processed successfully, results stored at {spleeterOutputPath}."})

            return JSONResponse(status_code=200, content={"message": f"MIDI file generated successfully at {basicPitchOutputPath}"})
        except Exception as e:
            logging.exception("An unexpected error occurred during separation")
            return JSONResponse(status_code=500, content={"message": f"An error occurred during separation: {str(e)}"})
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.exception("An unexpected error occurred during file handling")
        return JSONResponse(status_code=500, content={"message": f"An error occurred during file handling: {str(e)}"})


if __name__ == "__main__":
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    uvicorn.run(app, host="0.0.0.0", port=5000)
