import logging
import os

import uvicorn
from fastapi import HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from spleeter.separator import Separator
from basic_pitch.inference import predict_and_save

from CorsConfig import app
from database import SessionLocal
from models import MLEntity
from post_process import post_process

class MLDto(BaseModel):
    id: int
    model: str
    instrumentType: str
    fileName: str
    filePath: str
    email: str

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
async def getDto(mlDto: MLDto, db: Session = Depends(get_db)):
    id = mlDto.id
    model = mlDto.model
    instrumentType = mlDto.instrumentType
    fileName = mlDto.fileName # 확장자도 포함되어 있음
    inputFilePath = mlDto.filePath
    email = mlDto.email

    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Received DTO: %s", mlDto)

    # mlDto.id 로 entity Id 식별.
    ml_row = db.query(MLEntity).filter(MLEntity.id == id).first()

    if not ml_row:
        logging.error(f"No MLEntity found with ID {mlDto.id}")
        raise HTTPException(status_code=404, detail="MLEntity not found")

    # spleeter의 결과 path 정의 (확장자 제거)
    spleeterOutputPath = f"/spleeter_output/{email}/{fileName.split('.')[0]}"
    basicPitchOutputPath = f"/basic_pitch_output/{email}/{fileName.split('.')[0]}"
    musescoreOutputPath = f"musescore_output/{email}/{fileName.split('.')[0]}"

    ml_row.spleeter_output_path = spleeterOutputPath
    ml_row.basic_pitch_output_path = basicPitchOutputPath
    ml_row.musescore_output_path = musescoreOutputPath
    db.commit()

    try:
        if not os.path.exists(inputFilePath):
            raise HTTPException(status_code=404, detail="File not found")

        try:
            separator = Separator(f'spleeter:{model}')
            separator.separate_to_file(inputFilePath, spleeterOutputPath)

            instrumentFileName = "others.wav" if instrumentType == "guitar" else f"{instrumentType}.wav" # instrumentType이 guitar면 others.wav를 사용해야함.
            basicPitchInputPath = os.path.join(spleeterOutputPath, instrumentFileName)

            predict_and_save(
                [basicPitchInputPath],
                basicPitchOutputPath,
                save_midi=True
            )



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
    os.environ["CUDA_VISIBLE_DEVICES"] = "" # gpu 사용시에는 0이나 1 같은 nvidia-smi해서 나온 결과의 gpu # 작성
    uvicorn.run(app, host="0.0.0.0", port=5000)
