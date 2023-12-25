import sys
import os.path
import time
import shutil
import urllib.request
import base64
from datetime import datetime
import io
import json
from PIL import Image
# from flask import Flask, render_template, request
from dbconfig import add_db_log, add_group, \
    delete_face, delete_group_db, \
    get_all_faces, get_faces_group, get_group_cnt, \
    get_group_rows, get_groupID, get_logs, get_user_id_by_key, \
    register_face, set_server, record_log
from insightface.app import FaceAnalysis
import os
import numpy as np
from paddleocr import PaddleOCR
from json.decoder import JSONDecodeError
from insightface.utils.face_align import norm_crop
from lightqnet.evaluate import evaluate
import cv2
from inspect import currentframe, getframeinfo
from utils import (RESULT_DB_CONNECTION_ERROR, RESULT_FACE_REGISTER_FAIL_MORE_THAN_ONE_FACE, \
                   RESULT_FILE_ERROR, RESULT_INPUT_ERROR, RESULT_INVALID_CONFIGURATION, \
                    RESULT_INVALID_PRIVILIEGE, RESULT_NO_FACE_DETECTED, RESULT_NO_GROUP_EXIST, RESULT_NO_RESULT, \
                    RESULT_POOR_QUALITY, RESULT_SUCCESS, RESULT_UNKNOWN_ERROR, compare_face, \
                    get_admin_setting, get_config_val, get_configuration, \
                    get_error_name, get_error_response, identify_face)
from fastapi import FastAPI, Form, File, UploadFile
import uvicorn
from typing_extensions import Annotated
from fastapi.middleware.cors import CORSMiddleware
from multiprocessing import set_start_method
from multiprocessing import Process, Manager
try:
    set_start_method('spawn')
except RuntimeError:
    pass

global app
app = FastAPI()
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

faceapp = FaceAnalysis(name='buffalo_sc', root='.')
faceapp.prepare(ctx_id=0, det_thresh=0.5, det_size=(640, 640))
dir_path = os.path.dirname(os.path.realpath(__file__))
ocr = PaddleOCR(lang='ch') 

db_server = get_admin_setting("db_server")
if type(db_server) is int and db_server < 0:
    frameinfo = getframeinfo(currentframe())
    record_log("", "Invalid admin settings", frameinfo.filename + " at line:" + str(frameinfo.lineno) )
    
db_user = get_admin_setting("db_user_id")
if type(db_user) is int and db_user < 0:
    frameinfo = getframeinfo(currentframe())
    record_log("", "Invalid admin settings", frameinfo.filename + " at line:" + str(frameinfo.lineno) )

db_password = get_admin_setting("db_user_password")
if type(db_password) is int and db_password < 0:
    frameinfo = getframeinfo(currentframe())
    record_log("", "Invalid admin settings", frameinfo.filename + " at line:" + str(frameinfo.lineno) )

db_name = get_admin_setting("db_name")
if type(db_name) is int and db_name < 0:
    frameinfo = getframeinfo(currentframe())
    record_log("", "Invalid admin settings", frameinfo.filename + " at line:" + str(frameinfo.lineno) )

server_connected = set_server(db_server, db_user, db_password, db_name)

if type(server_connected) is int and server_connected == RESULT_DB_CONNECTION_ERROR:
    frameinfo = getframeinfo(currentframe())
    record_log("", "Invalid admin settings", frameinfo.filename + " at line:" + str(frameinfo.lineno) )

def verify_user(key):
    if key.strip() == "":
        return 0
    if verify_admin(key):
        return 1

def verify_admin(key):
    verified = False
    admin_key = get_admin_setting("admin_key")
    if type(admin_key) is int and  admin_key < 0:
        return False
    if key == admin_key:
        verified = True
    return verified

def set_configuration(config, val):
    configurations = get_configuration()
    try:
        with open("configuration.json", 'w+') as file:
            configurations[config] = str(val)
            file.truncate()
            json.dump(configurations, file, indent=4)
            return RESULT_SUCCESS
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        record_log("", str(e), frameinfo.filename + " at line:" + str(frameinfo.lineno) )
        return RESULT_FILE_ERROR

quality_due = float(get_config_val('image_quality_due'))
global_threshold = int(get_config_val("match_threshold"))

@app.get("/groups")
def get_groups(key: Annotated[str, Form()], ):
    if verify_user(key) != 1:
        return get_error_response(RESULT_INVALID_PRIVILIEGE)
    rows = get_group_rows()
    
    try:
        if type(rows) is int and rows < 0:
            add_log("", "groups", rows, get_error_name(rows))
            return get_error_response(rows)
        else:
            add_log("", "groups")
            return ({"status": "success", "result": rows})
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        record_log("groups", str(e), frameinfo.filename + " at line:" + str(frameinfo.lineno) )
        return get_error_response(RESULT_UNKNOWN_ERROR)

@app.get('/groupnum')
def get_group_num(key: Annotated[str, Form()] ):
    if verify_user(key) != 1:
        return get_error_response(RESULT_INVALID_PRIVILIEGE)
    cnt = get_group_cnt()
    add_log("", "groupnum", cnt, get_error_name(cnt))
    if cnt >= 0:
        return ({"status": "success", "result": cnt})
    else:
        return get_error_response(cnt)

@app.get('/list')
def get_faces(key: Annotated[str, Form()], page: Annotated[int, Form()], 
                    limit: Annotated[int, Form()], group: Annotated[str, Form()],
                    order: Annotated[str, Form()], attach_image: Annotated[int, Form()] ):
    if verify_user(key) != 1:
        return get_error_response(RESULT_INVALID_PRIVILIEGE)
    if order.strip() == "":
        order = 'createdOn desc'
    rows = get_faces_group(group, page, limit, order)
    if type(rows) is int and rows < 0:
        return get_error_response(rows)
    try:
        result = []
        for row in rows:
            if attach_image == 1:
                # if not os.path.exists(dir_path + "\\faces\\face_db\\" + str(group)):
                #     os.makedirs(dir_path + "\\faces\\face_db\\" + str(group))

                # imagepath = dir_path + "\\faces\\face_db\\" + str(group) + "\\" + str(row.face_id) + ".jpg"
                try:
                    # im = Image.open(imagepath)
                    # data = io.BytesIO()
                    # im.save(data, "JPEG")
                    # encoded_img_data = base64.b64encode(data.getvalue())

                    # "image" : encoded_img_data.decode('utf-8')
                    result.append({
                        "face_id" : row.face_id,
                        "group" : group,
                        "image" : ""
                    })
                except:
                    result.append({
                        "face_id" : row.face_id,
                        "group" : group,
                        "image" : ""
                    })
            else:
                result.append({
                        "face_id" : row.face_id,
                        "group" : group
                    })
        add_log("", "list", 1, "group="+str(group))
        return ({"status": "success", "result": result})
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        record_log("list", str(e), frameinfo.filename + " at line:" + str(frameinfo.lineno) )
        return get_error_response(RESULT_UNKNOWN_ERROR)

@app.post('/setconfig')
def setconfig(key: Annotated[str, Form()], config: Annotated[str, Form()], 
                    value: Annotated[str, Form()]):
    if not verify_admin(key):
        return get_error_response(RESULT_INVALID_PRIVILIEGE)
    ret = set_configuration(config, value)
    
    if type(ret) is int and ret < 0:
        add_log("", "setconfig", ret, "config="+config +";value="+str(value))
        return get_error_response(ret)
    else:
        add_log("", "setconfig", 1, "config="+config +";value="+str(value))
        return ({"status": "success"})

@app.get('/getconfig')
def getconfig(key: Annotated[str, Form()], config: Annotated[str, Form()]):
    if not verify_admin(key):
        return get_error_response(RESULT_INVALID_PRIVILIEGE)
    val = get_config_val(config)
    if type(val) is int and val < 0:
        add_log("", "getconfig", val, "config="+config)
        return get_error_response(val)
    else:
        add_log("", "getconfig", 1, "config="+config+";value="+str(val))
        return ({"status": "success", "result": str(val)})

@app.post('/register')
def register_user_face(key: Annotated[str, Form()], id: Annotated[str, Form()],
                             file: Annotated[UploadFile, File()], group: Annotated[str, Form()]):
    global faceapp
    face_id = id
    face_group = group
    if not verify_admin(key):
        return get_error_response(RESULT_INVALID_PRIVILIEGE)
    group_id = get_groupID(face_group)
    if type(group_id) is int and group_id < 0:
        return get_error_response(group_id)
    # bStoreFaceImage = 0
    # if not os.path.exists(dir_path + "\\faces\\_failed_registration"):
    #     os.makedirs(dir_path + "\\faces\\_failed_registration")
    img_array = np.asarray(bytearray(file.file.read()), dtype=np.uint8)
    initial_image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    try:
        faces, input_image, offset = get_faces_from_image(initial_image)
        if len(faces) == 1:
            # if not os.path.exists(dir_path + "\\faces\\face_db\\" + face_group):
            #     os.makedirs(dir_path + "\\faces\\face_db\\" + face_group)
            # imagename = dir_path + "\\faces\\face_db\\" + face_group + "\\" + face_id + ".jpg"
            
            aligned_face = norm_crop(input_image, faces[0].kps, 112)
            resized_image = cv2.resize(aligned_face, (96, 96))
            # if bStoreFaceImage == 1:
            #     cv2.imwrite(imagename, resized_image)
            eval_image = evaluate(resized_image)
            if eval_image < quality_due:
                add_log("", "register", RESULT_POOR_QUALITY, "quality="+str(eval_image))
                return ({"status": "failed",
                                "errorcode": get_error_name(RESULT_POOR_QUALITY),
                                "result": str(eval_image)})
            
            embedding = faces[0].embedding
            str_embedding = embedding.astype(str)
            str_embedding = (str(str_embedding)).replace("'", "").replace("[", "").replace("]", "")
            ret = register_face(face_id, face_group, str_embedding)
            
            if type(ret) is int and ret < 0:
                add_log("", "register", ret, get_error_name(ret))
                return get_error_response(ret)
            else:
                add_log("", "register", 1, "quality="+str(eval_image))
                return ({"status": "success",
                            "result": str(eval_image)})
        elif len(faces) > 1:
            for face in faces:
                box = face.bbox.astype(np.int)
                # cv2.rectangle(input_image, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 1)
            # cv2.imwrite(temp_image_path, input_image)
            add_log("", "register", RESULT_FACE_REGISTER_FAIL_MORE_THAN_ONE_FACE, get_error_name(RESULT_FACE_REGISTER_FAIL_MORE_THAN_ONE_FACE))
            return get_error_response(RESULT_FACE_REGISTER_FAIL_MORE_THAN_ONE_FACE)
        else:
            add_log("", "register", RESULT_NO_RESULT, get_error_name(RESULT_NO_RESULT))
            return get_error_response(RESULT_NO_RESULT)
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        record_log("register", str(e), frameinfo.filename + " at line:" + str(frameinfo.lineno) )
        return get_error_response(RESULT_UNKNOWN_ERROR)

@app.post('/unregister')
def unregister_user_face(key: Annotated[str, Form()], id: Annotated[str, Form()],
                             group: Annotated[str, Form()]):
    face_id = id
    face_group = group
    if not verify_admin(key):
        return get_error_response(RESULT_INVALID_PRIVILIEGE)
    try:
        ret = delete_face(face_id, face_group)
        if type(ret) is int and ret < 0:
            add_log("", "unregister", ret, "group="+str(face_group)+";id="+str(face_id))
            return get_error_response(ret)
        imagename = dir_path + "\\faces\\face_db\\" + face_group + "\\" + face_id + ".jpg"
        add_log("", "unregister", 1, "group="+str(face_group)+";id="+str(face_id))
        if os.path.isfile(imagename):
            # im = Image.open(imagename)
            # data = io.BytesIO()
            # im.save(data, "JPEG")
            # encoded_img_data = base64.b64encode(data.getvalue())
            try:
                os.remove(imagename)
            except:
                pass
            return ({"status": "success"})
                        # "image": encoded_img_data.decode('utf-8')})
        else:
            return ({"status": "success"})
                        # "image": ""})
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        record_log("unregister", str(e), frameinfo.filename + " at line:" + str(frameinfo.lineno) )
        return get_error_response(RESULT_UNKNOWN_ERROR)

@app.get('/getlog')
def getlog(key: Annotated[str, Form()], page: Annotated[int, Form()],
                             limit: Annotated[int, Form()], order: Annotated[str, Form()],
                             action_type: Annotated[str, Form()], success: Annotated[int, Form()]):
    if not verify_admin(key):
        return get_error_response(RESULT_INVALID_PRIVILIEGE)
    rows = get_logs(page, limit, action_type, order, success)
    if not rows:
        return ({"status": "success", "result": "RESULT_NO_RESULT"})
    if type(rows) is int and rows < 0:
        return get_error_response(rows)
    result = []
    for row in rows:
        result.append([row.user_action, str(row.createdOn), row.success, row.comment])
    return ({"status": "success", "result": result})

def add_log(key, action_type, success=1, comment=""):
    is_log = int(get_config_val("log"))
    if is_log != 1:
        return
    add_db_log(key, action_type, success, comment)

@app.post('/addgroup')
def add_new_group(key: Annotated[str, Form()], id: Annotated[str, Form()]):
    if not verify_admin(key):
        return get_error_response(RESULT_INVALID_PRIVILIEGE)
    group_id = id
    result = add_group(group_id)
    if type(result) is int and result < 0:
        add_log("", "addgroup", result, "group="+str(group_id))
        return get_error_response(result)
    else:
        add_log("", "addgroup", 1, "group="+str(group_id))
        return ({"status": "success"})

@app.post('/delete_group')
def delete_group(key: Annotated[str, Form()], group: Annotated[str, Form()]):
    if not verify_admin(key):
        return get_error_response(RESULT_INVALID_PRIVILIEGE)
    ret = delete_group_db(group)
    if type(ret) is int and ret < 0:
        add_log("", "delete_group", ret, "group="+str(group))
        return get_error_response(ret)
    else:
        add_log("", "delete_group", 1, "group="+str(group))
        try:
            shutil.rmtree(dir_path + "\\faces\\face_db\\" + group)
        except:
            pass
        return ({"status": "success"})


def get_faces_from_image(input_image):
    new_image = input_image
    faces = faceapp.get(new_image)
    if len(faces) == 0:
        hei, wid, channels = input_image.shape
        large_wid, large_hei = int(wid+100), int(hei+100)
        new_image = np.zeros((large_hei, large_wid, channels), np.uint8)
        new_image[::] = 255
        x_offset = int((large_wid - wid) / 2)
        y_offset = int((large_hei - hei) / 2)
        new_image[y_offset:y_offset+input_image.shape[0], 
                    x_offset:x_offset+input_image.shape[1]] = input_image
        new_faces = faceapp.get(new_image)
        if len(new_faces) == 0:
            return [], 0, 0
        else:
            return new_faces, new_image, 50
    return faces, new_image, 0

def func_detect_faces(initial_image, attach_image, tmp_path):
    bStoreImage = 0
    try:
        faces, input_image, offset = get_faces_from_image(initial_image)
        result = []
        if len(faces) > 0:
            face_i = 1
            for face in faces:
                box = face.bbox.astype(np.int)
                color = (0, 0, 255)

                aligned_face = norm_crop(input_image, face.kps, 112)

                eval_face = cv2.resize(aligned_face, (96, 96))
                eval_image = evaluate(eval_face)
                # cv2.imwrite(dir_path + "\\detected_face-"+str(face_i)+ "-" + str(eval_image) + ".jpg", eval_face)
                face_i += 1

                result.append({
                    "confidence": str(eval_image),
                    "x_topleft": str(box[0] - offset),
                    "y_topleft": str(box[1] - offset),
                    "x_bottomright": str(box[2] - offset),
                    "y_bottomright": str(box[3] - offset)
                })

                # if bStoreImage == 1:
                # cv2.rectangle(input_image, (box[0], box[1]), (box[2], box[3]), color, 2)
                # cv2.putText(input_image, str(eval_image), 
                #             (box[0], box[1]-1), cv2.FORMATTER_FMT_NUMPY, 0.5, (255, 0, 0), 1)
            # if bStoreImage == 1:
                # cv2.imwrite(tmp_path, input_image)
        else:
            add_log("", "detectfaces", RESULT_NO_RESULT)
            return ({"status": "success", "count" : "0"})
        add_log("", "detectfaces", 1)
        encoded_img_data = ""
        if attach_image == 1:
            is_success, buf = cv2.imencode(".jpg", input_image)
            data = io.BytesIO(buf)
            encoded_img_data = base64.b64encode(data.getvalue())
            return ({"status": "success",
                    "count" : str(len(result)),
                    "result": {"facelist": result},
                    "image" : encoded_img_data.decode('utf-8')})
        else:
            return ({"status": "success",
                    "count" : str(len(result)),
                    "result": {"facelist": result}})
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        record_log("detectfaces", str(e), frameinfo.filename + " at line:" + str(frameinfo.lineno) )
        return get_error_response(RESULT_UNKNOWN_ERROR)

@app.get('/detectfaces_url')
def detect_faces_url(key: Annotated[str, Form()], file: Annotated[str, Form()],
                       attach_image: Annotated[int, Form()]):
    if verify_user(key) != 1:
        return get_error_response(RESULT_INVALID_PRIVILIEGE)    
    try:
        # now = datetime.now()
        # dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
        # user_id = get_user_id_by_key(key)
        # if not os.path.exists(dir_path + "\\faces\\_detect_logs"):
        #     os.makedirs(dir_path + "\\faces\\_detect_logs")
        # if verify_admin(key):
        #     tmp_path = dir_path + "\\faces\\_detect_logs\\" + dt_string + "__admin.jpg"
        # else:
        #     tmp_path = dir_path + "\\faces\\_detect_logs\\" + dt_string + "__" + user_id + ".jpg"
        tmp_path = ""
        
        url_resp = ""
        try:
            url_resp = urllib.request.urlopen(file)
        except:
            try:
                url_resp = urllib.request.urlopen(file)
            except:
                return get_error_response(RESULT_INPUT_ERROR)
        
        image = cv2.imdecode(np.array(bytearray(url_resp.read()), dtype=np.uint8), cv2.IMREAD_COLOR)
        ret = func_detect_faces(image, attach_image, tmp_path)
        return ret
    except:
        return get_error_response(RESULT_FILE_ERROR)

@app.get('/compare')
def compare_faces(key: Annotated[str, Form()], file1: Annotated[UploadFile, File()],
                       file2: Annotated[UploadFile, File()]):
    global faceapp
    if verify_user(key) != 1:
        return get_error_response(RESULT_INVALID_PRIVILIEGE)
    try:
        now = datetime.now()
        dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
        user_id = get_user_id_by_key(key)
        # if not os.path.exists(dir_path + "\\faces\\_compare_logs"):
        #     os.makedirs(dir_path + "\\faces\\_compare_logs")
        img_array1 = np.asarray(bytearray(file1.file.read()), dtype=np.uint8)
        initial_image1 = cv2.imdecode(img_array1, cv2.IMREAD_COLOR)

        img_array2 = np.asarray(bytearray(file2.file.read()), dtype=np.uint8)
        initial_image2 = cv2.imdecode(img_array2, cv2.IMREAD_COLOR)

        ret = func_compare_faces(image1=initial_image1, image2=initial_image2)
        return ret
    except:
        return get_error_response(RESULT_FILE_ERROR)
        
def func_compare_faces(image1, image2):
    try:
        faces1, input_image1, offset1 = get_faces_from_image(image1)
        faces2, input_image2, offset2 = get_faces_from_image(image2)
        if len(faces1) > 1:
            return {"status": "failed", "result": "file1 has more than 1 faces"}
        elif len(faces1) == 0:
            return {"status": "failed", "result": "file1 has no faces"}
        if len(faces2) > 1:
            return {"status": "failed", "result": "file2 has more than 1 faces"}
        elif len(faces2) == 0:
            return {"status": "failed", "result": "file2 has no faces"}
    
        face1 = faces1[0]
        face2 = faces2[0]
        similarity = compare_face(face1.embedding, face2.embedding)
        return {"status":"success", "result": str(similarity)}
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        record_log("compare", str(e), frameinfo.filename + " at line:" + str(frameinfo.lineno) )
        return get_error_response(RESULT_UNKNOWN_ERROR)

@app.get('/detectfaces')
def detect_faces(key: Annotated[str, Form()], file: Annotated[UploadFile, File()],
                       attach_image: Annotated[int, Form()]):
    global faceapp
    if verify_user(key) != 1:
        return get_error_response(RESULT_INVALID_PRIVILIEGE)
    try:
        # now = datetime.now()
        # dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
        # user_id = get_user_id_by_key(key)
        # if not os.path.exists(dir_path + "\\faces\\_detect_logs"):
        #     os.makedirs(dir_path + "\\faces\\_detect_logs")
        # if verify_admin(key):
        #     tmp_path = dir_path + "\\faces\\_detect_logs\\" + dt_string + "__admin.jpg"
        # else:
        #     tmp_path = dir_path + "\\faces\\_detect_logs\\" + dt_string + "__" + user_id + ".jpg"
        tmp_path = ""

        img_array = np.asarray(bytearray(file.file.read()), dtype=np.uint8)
        initial_image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        ret = func_detect_faces(initial_image=initial_image, attach_image=attach_image, tmp_path=tmp_path)
        return ret
    except:
        return get_error_response(RESULT_FILE_ERROR)

def func_search_face(input_image, group, attach_image, tmp_path, threshold):
    # face_groups = get_group_rows()
    # if not group in face_groups:
    #     add_log("", "searchface", RESULT_NO_GROUP_EXIST, "group="+str(group))
    #     return get_error_response(RESULT_NO_GROUP_EXIST)
    # try:
    #     os.remove(tmp_path)
    # except Exception as e:
    #     pass
    faces, ret_image, offset = get_faces_from_image(input_image)
    if threshold <= 0:
        add_log("", "searchface", RESULT_INVALID_CONFIGURATION, "threshold=" + str(threshold))
        return get_error_response(RESULT_INVALID_CONFIGURATION)
    tmp_index = 1
    result = []

    # try:
    if len(faces) > 0:
        for face in faces:
            detected_ids = []
            box = face.bbox.astype(np.int)
            face_image = ret_image[box[1]: box[3], box[0]:box[2]]

            try:
                if face_image.shape[0] == 0 or face_image.shape[1] == 0:
                    continue
            except Exception as e:
                record_log("searchface", str(e), frameinfo.filename + " at line:" + str(frameinfo.lineno) )
                return get_error_response(RESULT_INPUT_ERROR)

            aligned_face = norm_crop(ret_image, face.kps, 112)
            eval_face = cv2.resize(aligned_face, (96, 96))
            eval_image = evaluate(eval_face)
            tmp_index += 1

            page_iter = 1
            while True:
                rows = get_faces_group(group, page_iter, 30)
                if type(rows) is int and rows < 0:
                    return get_error_response(rows)

                try:
                    if len(rows) == 0:
                        break
                except :
                    break

                page_iter += 1
                for row in rows:
                    try:
                        face_fature = row.face_vector
                        face_featurelist = face_fature.split()
                        face_featurelist = [float(i) for i in face_featurelist]
                        face_id, similarity = identify_face(threshold, 
                                                            embedding=face.embedding, 
                                                            embedding_dict=[face_featurelist, row.face_id])
                        if face_id != "":
                            detected_ids.append({
                                "id": face_id,
                                "similaritylevel": str(similarity)})
                    except Exception as e:
                        record_log("searchface", str(e), frameinfo.filename + " at line:" + str(frameinfo.lineno) )
                        return get_error_response(RESULT_UNKNOWN_ERROR)
                        
            if attach_image == 1:
                try:
                    is_success, buf = cv2.imencode(".jpg", face_image)
                    data = io.BytesIO(buf)
                    encoded_img_data = base64.b64encode(data.getvalue())                    
                    result.append({
                        "similarfacesfound": str(len(detected_ids)),
                        "similarfaceresult": detected_ids,
                        "x_topleft":  str(box[0]-offset),
                        "y_topleft": str(box[1]-offset),
                        "x_bottomright": str(box[2]-offset),
                        "y_bottomright": str(box[3]-offset),
                        "quality": str(eval_image),
                        "image": encoded_img_data.decode('utf-8')
                    })
                except Exception as e:
                    record_log("searchface", str(e), frameinfo.filename + " at line:" + str(frameinfo.lineno) )
                    return get_error_response(RESULT_FILE_ERROR)
            else:
                result.append({
                    "similarfacesfound": str(len(detected_ids)),
                    "similarfaceresult": detected_ids,
                    "x_topleft":  str(box[0]-offset),
                    "y_topleft": str(box[1]-offset),
                    "x_bottomright": str(box[2]-offset),
                    "y_bottomright": str(box[3]-offset),
                    "quality": str(eval_image)
                })
    else:
        add_log("", "searchface", RESULT_NO_RESULT, get_error_name(RESULT_NO_RESULT))
        return ({"status": "success",
                        "facecount": 0,
                        "result": []})
    
    add_log("", "searchface")
    return ({"status": "success",
                        "facecount": len(faces),
                        "result": result})
    # except Exception as e:
    #     frameinfo = getframeinfo(currentframe())
    #     record_log("searchface", str(e), frameinfo.filename + " at line:" + str(frameinfo.lineno) )
    #     return get_error_response(RESULT_UNKNOWN_ERROR)

@app.get('/searchface_url')
def search_face_url(key: Annotated[str, Form()], file: Annotated[str, Form()],
                      group: Annotated[str, Form()], attach_image: Annotated[int, Form()], threshold: Annotated[int, Form()]):
    if verify_user(key) != 1:
        return get_error_response(RESULT_INVALID_PRIVILIEGE)
    
    # now = datetime.now()
    # dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
    # user_id = get_user_id_by_key(key)
    # if not os.path.exists(dir_path + "\\faces\\_detect_logs"):
    #     os.makedirs(dir_path + "\\faces\\_detect_logs")
    # if verify_admin(key):
    #     tmp_path = dir_path + "\\faces\\_detect_logs\\" + dt_string + "__admin.jpg"
    # else:
    #     tmp_path = dir_path + "\\faces\\_detect_logs\\" + dt_string + "__" + user_id + ".jpg"    
    tmp_path = ""
    url_resp = ""
    try:
        url_resp = urllib.request.urlopen(file)
    except:
        try:
            # time.sleep(0.5)
            url_resp = urllib.request.urlopen(file)
        except:
            return get_error_response(RESULT_INPUT_ERROR)
        
    try:
        image = cv2.imdecode(np.array(bytearray(url_resp.read()), dtype=np.uint8), cv2.IMREAD_COLOR)
        if threshold == 0:
            threshold = global_threshold
        ret = func_search_face(image, group, attach_image, tmp_path, threshold)
        return ret
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        record_log("searchface_url", str(e), frameinfo.filename + " at line:" + str(frameinfo.lineno) )
        return get_error_response(RESULT_FILE_ERROR)
    

@app.get('/searchface')
def search_face(key: Annotated[str, Form()], file: Annotated[UploadFile, File()],
                      group: Annotated[str, Form()], attach_image: Annotated[int, Form()]):
    global faceapp
    if verify_user(key) != 1:
        return get_error_response(RESULT_INVALID_PRIVILIEGE)
    
    try:
        # now = datetime.now()
        # dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
        # user_id = get_user_id_by_key(key)
        # if not os.path.exists(dir_path + "\\faces\\_detect_logs"):
        #     os.makedirs(dir_path + "\\faces\\_detect_logs")
        # if verify_admin(key):
        #     tmp_path = dir_path + "\\faces\\_detect_logs\\" + dt_string + "__admin.jpg"
        # else:
        #     tmp_path = dir_path + "\\faces\\_detect_logs\\" + dt_string + "__" + user_id + ".jpg"
        tmp_path = ""

        img_array = np.asarray(bytearray(file.file.read()), dtype=np.uint8)
        input_image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)        
        threshold = global_threshold
        ret = func_search_face(input_image, group, attach_image, tmp_path, threshold)
        return ret
    except:
        return get_error_response(RESULT_FILE_ERROR)

def func_detect_ocr(input_image, attach_image, tmp_path):
    # try:
    #     os.remove(tmp_path)
    # except:
    #     pass    
    try:
        bStoreImage = 0
        ocr_result = []
        result = ocr.ocr(input_image)
        if len(result) > 0 :
            for line in result[0]:
                p1 = line[0][0]
                p2 = line[0][2]
                # cv2.rectangle(input_image, (round(p1[0]), round(p1[1])), (round(p2[0]), round(p2[1])), (255, 0, 0), 2)
                if round(line[1][1], 2) > 0.5:
                    ocr_result.append(line[1][0])
        is_success, buf = cv2.imencode(".jpg", input_image)
        data = io.BytesIO(buf)
        encoded_img_data = base64.b64encode(data.getvalue())
        add_log("", "detectocr")
        if attach_image == 1:
            return ({"status": "success",
                        "result": ocr_result,
                        "image": encoded_img_data.decode('utf-8')})
        else:
            return ({"status": "success",
                        "result": ocr_result, "image": ""})
    except Exception as e:
        frameinfo = getframeinfo(currentframe())
        record_log("detectocr", str(e), frameinfo.filename + " at line:" + str(frameinfo.lineno) )
        return get_error_response(RESULT_UNKNOWN_ERROR)    

@app.get('/detectocr_url')
def ocr_image_url(key: Annotated[str, Form()], file: Annotated[str, Form()],
                      attach_image: Annotated[int, Form()]):
    if verify_user(key) != 1:
        return get_error_response(RESULT_INVALID_PRIVILIEGE)
    # now = datetime.now()
    # dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
    # user_id = get_user_id_by_key(key)
    # if not os.path.exists(dir_path + "/ocr/_detect_logs"):
    #     os.makedirs(dir_path + "/ocr/_detect_logs")
    # if verify_admin(key):
    #     tmp_path = dir_path + "/ocr/_detect_logs/" + dt_string + "__admin.jpg"
    # else:
    #     tmp_path = dir_path + "/ocr/_detect_logs/" + dt_string + "__" + user_id + ".jpg"
    tmp_path = ""
    url_resp = ""
    try:
        url_resp = urllib.request.urlopen(file)
    except:
        try:
            url_resp = urllib.request.urlopen(file)
        except:
            return get_error_response(RESULT_INPUT_ERROR)
    image = cv2.imdecode(np.array(bytearray(url_resp.read()), dtype=np.uint8), cv2.IMREAD_COLOR)    
    
    ret = func_detect_ocr(image, attach_image, tmp_path)
    return ret                        


@app.get('/detectocr')
def ocr_image_upload(key: Annotated[str, Form()], file: Annotated[UploadFile, File()],
                      attach_image: Annotated[int, Form()]):
    # global ocr
    if verify_user(key) != 1:
        return get_error_response(RESULT_INVALID_PRIVILIEGE)
    now = datetime.now()
    dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
    user_id = get_user_id_by_key(key)
    if not os.path.exists(dir_path + "/ocr/_detect_logs"):
        os.makedirs(dir_path + "/ocr/_detect_logs")
    if verify_admin(key):
        tmp_path = dir_path + "/ocr/_detect_logs/" + dt_string + "__admin.jpg"
    else:
        tmp_path = dir_path + "/ocr/_detect_logs/" + dt_string + "__" + user_id + ".jpg"
    img_array = np.asarray(bytearray(file.file.read()), dtype=np.uint8)
    input_image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    ret = func_detect_ocr(input_image, attach_image, tmp_path)
    return ret

if __name__ == '__main__':
    uvicorn.run("app:app", 
                host="0.0.0.0", 
                port=5000, 
                http="httptools", 
                interface="asgi3",  
                timeout_keep_alive=6000,
                workers=1,
    )
