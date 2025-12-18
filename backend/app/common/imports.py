from fastapi import APIRouter, Request, Depends, HTTPException, Cookie, FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import jwt
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
import json
import os
import httpx
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import time
from sqlalchemy.exc import IntegrityError
import cipher
from cryptography.fernet import Fernet
from jwt import ExpiredSignatureError
from dotenv import load_dotenv

load_dotenv() 