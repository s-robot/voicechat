from vox_service import VoxService

vs = VoxService()
# fillvoices = ["そっかそっか", "そうかぁー", "そうだねー", "えっとぉー", "えっとねぇー", "うーんとね"]
fillvoices = ["じゃあね", "またね", "元気でね", "また話そうね", "バイバイ"]
for f in fillvoices:
    vs.voxvoice(f, 0, save=True)
