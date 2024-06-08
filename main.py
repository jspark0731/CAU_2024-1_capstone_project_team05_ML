import os
import uvicorn
from fastapi import HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from spleeter.separator import Separator
import logging

from CorsConfig import app

class MLDto(BaseModel):
    model: str
    instrumentType: str
    fileName: str
    filePath: str
    email: str


@app.post("/api/ml/getFile")
async def getDto(mlDto: MLDto):
    inputFilePath = mlDto.filePath
    fileName = mlDto.fileName
    email = mlDto.email
    model = mlDto.model

    # spleeter의 결과 path 정의
    spleeterOutputPath = f"/spleeter_output/{email}/{fileName}"
    basicPitchOutputPath = f"/basic_pitch_output/{email}/{fileName}"

    try:
        if not os.path.exists(inputFilePath):
            raise HTTPException(status_code=404, detail="File not found")

        try:
            separator = Separator(f'spleeter:{model}')
            separator.separate_to_file(inputFilePath, spleeterOutputPath)

            return JSONResponse(status_code=200, content={"message": f"File '{fileName}' processed successfully."})
        except HTTPException as e:
            raise e
        except Exception as e:
            logging.exception("An unexpected error occurred")
            return JSONResponse(status_code=500, content={"message": f"An error occurred: {str(e)}"})
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.exception("An unexpected error occurred")
        return JSONResponse(status_code=500, content={"message": f"An error occurred: {str(e)}"})

if __name__ == "__main__":
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    uvicorn.run(app, host="0.0.0.0", port=5000)
