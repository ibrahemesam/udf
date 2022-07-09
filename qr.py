from subprocess import check_output as co
def qr(string, margin=2):
    return co(['qrencode', '-m', str(margin), '-t', 'utf8', string]).decode().strip()
