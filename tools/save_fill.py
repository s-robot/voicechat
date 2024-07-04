import os
import sys

parent = os.path.dirname(os.path.dirname(__file__))
sys.path.append(parent)

from vox_service import VoxService

vs = VoxService()
fillvoices = ["じゃあね", "またね", "元気でね", "また話そうね", "バイバイ"]
for f in fillvoices:
    vs.voxvoice(f, 0, save=True)
