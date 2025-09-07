#!/bin/bash
apt-get update
apt-get install -y tesseract-ocr tesseract-ocr-vie
python3 main.py
