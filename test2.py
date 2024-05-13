from vox_service import VoxService

vs = VoxService()
fillvoices = ["そっかそっか", "そうかぁー", "そうだねー", "えっとぉー", "えっとねぇー", "うーんとね"]

for f in fillvoices:
    vs.voxvoice(f, 0, save=True)
