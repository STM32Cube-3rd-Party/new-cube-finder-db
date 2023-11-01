# !/usr/bin/env python3
"""
将原始数据库的blob字段转换为字符串
"""

import sys
import os
import json
import base64


if __name__ == '__main__':
    with open('feature.json', 'r+') as f:
        data = json.load(f)
        for obj in data:
            obj['name'] = base64.b64decode(obj['name']).decode('utf-8')

    with open('feature.json', 'w') as f:
        f.write(json.dumps(data, indent=4))
    
    with open('featureitem.json', 'r+') as f:
        data = json.load(f)
        for obj in data:
            obj['item'] = base64.b64decode(obj['item']).decode('utf-8')
    
    with open('featureitem.json', 'w') as f:
        f.write(json.dumps(data, indent=4))