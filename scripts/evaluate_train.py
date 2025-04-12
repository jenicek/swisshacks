import requests
import json
import time
from dotenv import load_dotenv
import hashlib
from pathlib import Path
from typing import List, Dict, Any
import base64
from openai import AzureOpenAI
from pprint import pprint

import trainset
from data_parsing import parse_pdf_banking_form, parse_docx, parse_txt
from client_data.client_data import ClientData
from model.rule_based_model import SimpleModel


def eval_on_trainset():
    trainiter = trainset.TrainIterator(limit=100, maxkey=1000)
    rule_based_model = SimpleModel()

    for path in trainiter:
        input_dir = Path(path)
        identifier = path.split('/')[-1]

        with open(input_dir / "account.pdf", "rb") as file:
            form = parse_pdf_banking_form.parse_banking_pdf(file.read())
        profile = json.loads(parse_docx.parse_docx_to_json(input_dir / "profile.docx"))
        description = parse_txt.parse_text_to_json(input_dir / "description.txt")
        with open(input_dir / "passport.json", "rb") as file:
            passport = json.loads(file.read())

        cd = ClientData(identifier, form, description, profile, passport)
        prediction = rule_based_model.predict(cd)

        trainiter.predict(prediction == 1)
        print(trainiter, input_dir)


if __name__ == "__main__":
    eval_on_trainset()
