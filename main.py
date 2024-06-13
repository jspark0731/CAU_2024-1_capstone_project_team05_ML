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
from models import SheetEntity, SheetEntity
from post_process import post_process

class MLDto(BaseModel):
    id: int
    model: str
    instrumentType: str
    fileName: str
    filePath: str
    email: str

class SheetDto(BaseModel):
    id: int
    email: str
    model: str
    instrumentType: str
    videoId: str
    fileName: str
    filePath: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/ml/ml_dto",)
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
    ml_row = db.query(SheetEntity).filter(SheetEntity.id == id).first()

    if not ml_row:
        logging.error(f"No MLEntity found with ID {mlDto.id}")
        raise HTTPException(status_code=404, detail="MLEntity not found")

    # spleeter의 결과 path 정의 (확장자 제거)
    spleeterOutputPath = f"/spleeter_output/{email.split('@')[0]}/{fileName.split('.')[0]}"
    basicPitchOutputPath = f"/basic_pitch_output/{email.split('@')[0]}/{fileName.split('.')[0]}"
    musescoreOutputPath = f"musescore_output/{email.split('@')[0]}/{fileName.split('.')[0]}"

    ml_row.spleeter_output_path = spleeterOutputPath
    ml_row.basic_pitch_output_path = basicPitchOutputPath
    ml_row.musescore_output_path = musescoreOutputPath
    db.commit()

    try:
        if not os.path.exists(inputFilePath):
            raise HTTPException(status_code=404, detail="File not found")

        try:
            # # spleeter
            # separator = Separator(f'spleeter:{model}')
            # separator.separate_to_file(inputFilePath, spleeterOutputPath)

            # 만약, instrumentType 이 guitar 면 output 중 others.wav 를 사용 해야함
            instrumentFileName = "others.wav" if instrumentType == "guitar" else f"{instrumentType}.wav" # instrumentType이 guitar면 others.wav를 사용해야함.
            basicPitchInputPath = os.path.join(spleeterOutputPath, instrumentFileName)

            # # basic-pitch -> 말고 onsets and frames?
            # predict_and_save(
            #     [basicPitchInputPath],
            #     basicPitchOutputPath,
            #     save_midi=True
            # )

            # musescore section

            # after musescore
            # if instrumentType == guitar -> post_process & is_lower
            # if instrumentType == base -> post_process & is_higher

            post_processed_xml = post_process(basicPitchOutputPath, f'{instrumentType}')

            return JSONResponse(status_code=200, content={"message": f"MIDI file generated successfully at {basicPitchOutputPath}"})

        except Exception as e:
            logging.exception("An unexpected error occurred during separation")
            return JSONResponse(status_code=500, content={"message": f"An error occurred during separation: {str(e)}"})
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.exception("An unexpected error occurred during file handling")
        return JSONResponse(status_code=500, content={"message": f"An error occurred during file handling: {str(e)}"})

@app.post("/api/ml/sheet_dto",)
async def getDto(sheetDto: SheetDto, db: Session = Depends(get_db)):
    id = sheetDto.id
    model = sheetDto.model
    instrumentType = sheetDto.instrumentType
    fileName = sheetDto.fileName # 확장자도 포함되어 있음
    inputFilePath = sheetDto.filePath
    email = sheetDto.email

    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Received DTO: %s", sheetDto)

    # Sheet.id 로 entity Id 식별.
    sheet_row = db.query(SheetEntity).filter(SheetEntity.id == id).first()

    if not sheet_row:
        logging.error(f"No MLEntity found with ID {sheetDto.id}")
        raise HTTPException(status_code=404, detail="MLEntity not found")

    # spleeter의 결과 path 정의 (확장자 제거)
    spleeterOutputPath = f"/spleeter_output/youtube/{email.split('@')[0]}/{fileName.split('.')[0]}"
    basicPitchOutputPath = f"/basic_pitch_output/youtube/{email.split('@')[0]}/{fileName.split('.')[0]}"
    musescoreOutputPath = f"musescore_output/youtube/{email.split('@')[0]}/{fileName.split('.')[0]}"

    sheet_row.spleeter_output_path = spleeterOutputPath
    sheet_row.basic_pitch_output_path = basicPitchOutputPath
    sheet_row.musescore_output_path = musescoreOutputPath
    db.commit()

    try:
        if not os.path.exists(inputFilePath):
            raise HTTPException(status_code=404, detail="File not found")

        try:
            # spleeter
            # separator = Separator(f'spleeter:{model}')
            # separator.separate_to_file(inputFilePath, spleeterOutputPath)

            # 만약, instrumentType 이 guitar 면 output 중 others.wav 를 사용 해야함
            instrumentFileName = "other.wav" if instrumentType == "guitar" else f"{instrumentType}.wav" # instrumentType이 guitar면 others.wav를 사용해야함.
            basicPitchInputPath = os.path.join(spleeterOutputPath, instrumentFileName)

            # # basic-pitch -> 말고 onsets and frames?
            # predict_and_save(
            #     [basicPitchInputPath],
            #     basicPitchOutputPath,
            #     save_midi=True
            # )

            # musescore section

            # after musescore
            # if instrumentType == guitar -> post_process & is_lower
            # if instrumentType == base -> post_process & is_higher

            # post_processed_xml = post_process(basicPitchOutputPath, f'{instrumentType}')

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
    os.environ["CUDA_VISIBLE_DEVICES"] = "" # gpu 사용 시에는 0이나 1 같은 nvidia-smi 해서 나온 결과의 gpu # 작성
    uvicorn.run(app, host="0.0.0.0", port=5000)
