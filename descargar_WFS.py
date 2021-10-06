import os
import requests
import argparse
import time
import random

def descarga_cosas(output_dir):
    maximo = 16832000
    rango = 1000000
    prefix = "FY_HY_"
    # Establecer debajo el inicio de la descarga
    for i in range(1000000, maximo, rango):
        # Nombre del archivo basado en el final de la url
        name = prefix + str(i) + '.xml'
        url = "https://inspire-wfs.maanmittauslaitos.fi/inspire-wfs/hy?request=GetFeature&version=2.0.0&service=WFS&TypeNames=hy-p:Watercourse&startIndex={}&count=1000000".format(i)
        # Establece la ruta absoluta del archivo
        local_file = os.path.join(output_dir, name)
        try:
            for n in range(100):
                # Petición url mediante librería requests
                req = requests.get(url, stream=True, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'})
                status = req.status_code
                if status == 400 and n < 99:
                #    time.sleep(random.random()*1)
                    print("error 400, reintentando n veces: {}".format(n))
                    continue
                elif status == 400 and n == 99:
                    print("Los elementos con initial index = {} no se han descargado".format(i))
                    print("¡¡El proceso se ha detenido!!")
                    return None
                elif status == 200:
                    with open(local_file, 'wb') as downloaded_file:
                        print ("descargando index: {}".format(i))
                        for chunk in req.iter_content(1024):
                            downloaded_file.write(chunk)
                  #  time.sleep(random.random()*1)
                    break
        except requests.exceptions.HTTPError as e:
            print("index fallido = {}".format(i), e)
        except requests.exceptions.ConnectionError as e:
            print("index fallido = {}".format(i), e)


def main(output_dir):
    descarga_cosas(output_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='url to process')

    parser.add_argument('-o', '--output', dest='outputdir', type=str,
                        help='Output directory to store the file')

    args = parser.parse_args()
    main(args.outputdir)
